/*
 * File taken from
 * http://www.asawicki.info/news_1468_circular_buffer_of_raw_binary_data_in_c.html
 * and modified to be thread safe for posix systems and to block on
 * write
 *
 * DESCRIPTION: Circular buffer to emulate an arbitrary sized pipe
 *              with blocking reads and writes.
 */

#include "cbuffer.h"

using namespace std;

CircularBuffer::CircularBuffer(size_t capacity)
    : beg_index_(0)
    , end_index_(0)
    , size_(0)
    , capacity_(capacity)
    , closed_(false)
{
    data_ = new char[capacity];
    if (pthread_cond_init(&space_cond_, NULL)){
        perror("error initializing space_cond_");
    }
    if (pthread_cond_init(&data_cond_, NULL)){
        perror("error initializing data_cond_");
    }
    if (pthread_mutex_init(&cond_mutex_, NULL)){
        perror("error initializing pthread_mutex");
    }
    if (pthread_mutex_init(&pointer_mutex_, NULL)){
        perror("error initializing pthread_mutex");
    }
}

CircularBuffer::~CircularBuffer()
{
    pthread_mutex_destroy(&pointer_mutex_);
    pthread_mutex_destroy(&cond_mutex_);
    pthread_cond_destroy(&space_cond_);
    pthread_cond_destroy(&data_cond_);
    delete [] data_;
}

/******************************************************************************
 * Writing data
 ******************************************************************************/

size_t CircularBuffer::write_nonblocking(const char *data, size_t bytes)
{
    /*
     *  write_nonblocking() - Non blocking write to buffer
     *
     *  Write to the circular buffer, if there is no space, do not
     *  block, but write 0 bytes.
     *
     *  returns: The number of bytes written to buffer on success, -1
     *  on failure.
     */
    if (closed_)   { return -1; }
    if (bytes == 0){ return  0; }

    /* Lock and calculate sizes */
    pthread_mutex_lock(&pointer_mutex_);
    size_t capacity        = capacity_;
    size_t bytes_to_write  = min(bytes, capacity - size_);
    size_t size_1          = capacity - end_index_;
    size_t size_2          = bytes_to_write - size_1;
    bool   single_step     = (bytes_to_write <= capacity - end_index_);
    pthread_mutex_unlock(&pointer_mutex_);

    /* Short circuit, there's no more space */
    if (bytes_to_write == 0){ return  0; }

    /* Write data */
    if (single_step){
        memcpy(data_ + end_index_, data, bytes_to_write);
    } else {
        memcpy(data_ + end_index_, data, size_1);
        memcpy(data_, data + size_1, size_2);
    }

    /* Update pointers */
    pthread_mutex_lock(&pointer_mutex_);
    if (single_step){
        end_index_ += bytes_to_write;
        if (end_index_ == capacity){
            /* Loop back */
            end_index_ = 0;
        }
    } else {
        end_index_ = size_2;
    }
    size_ += bytes_to_write;
    pthread_mutex_unlock(&pointer_mutex_);

    return bytes_to_write;
}

size_t CircularBuffer::write(const char *data, size_t bytes)
{
    /*
     *  write_nonblocking() - Blocking write to buffer
     *
     *  Write to the circular buffer, if there is not enough space
     *  write what we can and block until someone else has read from
     *  the buffer.
     *
     *  returns: The number of bytes written to buffer on success, -1
     *  on failure.
     */
    if (closed_)   { return -1; }
    if (bytes == 0){ return  0; }

    size_t bytes_written = 0;
    if (!has_space()){
        wait_for_space();
    }

    while (bytes_written < bytes){
        if (!has_space()){
            wait_for_space();
        }
        size_t written_this_time = write_nonblocking(data  + bytes_written,
                                                     bytes - bytes_written);
        bytes_written += written_this_time;
    }
    if (bytes_written > 0) {
        signal_data();
    }
    return bytes_written;
}

/******************************************************************************
 * Reading data
 ******************************************************************************/

size_t CircularBuffer::read_nonblocking(char *data, size_t bytes)
{
    /*
     *  read_nonblocking() - Nonblocking read from buffer
     *
     *  Read from the pipe at most size_t bytes.  If there is no data,
     *  read 0 bytes and immediately return 0;
     *
     *  returns: The number of bytes read from buffer on success, -1
     *  on failure.
     */
    if (closed_)   { return -1; }
    if (bytes == 0){ return  0; }

    pthread_mutex_lock(&pointer_mutex_);
    size_t capacity       = capacity_;
    size_t bytes_to_read  = min(bytes, size_);
    size_t size_1         = capacity - beg_index_;
    size_t size_2         = bytes_to_read - size_1;
    bool   single_step    = (bytes_to_read <= capacity - beg_index_);
    pthread_mutex_unlock(&pointer_mutex_);

    /* Read data */
    if (single_step){
        memcpy(data, data_ + beg_index_, bytes_to_read);
    } else {
        memcpy(data, data_ + beg_index_, size_1);
        memcpy(data + size_1, data_, size_2);
    }

    /* Update pointers */
    pthread_mutex_lock(&pointer_mutex_);
    if (single_step){
        beg_index_ += bytes_to_read;
        if (beg_index_ == capacity){
            /* Loop back */
            beg_index_ = 0;
        }
    } else {
        beg_index_ = size_2;
    }
    size_ -= bytes_to_read;
    pthread_mutex_unlock(&pointer_mutex_);

    return bytes_to_read;
}

size_t CircularBuffer::read(char *data, size_t bytes)
{
    /*
     *  read_nonblocking() - Blocking read from buffer
     *
     *  Read from the pipe at most size_t bytes.  If there is no data,
     *  wait for a signal saying somebody wrote to the pipe.
     *
     *  returns: The number of bytes read from buffer on success, -1
     *  on failure.
     */
    if (!size()){
        wait_for_data();
    }
    size_t bytes_read = read_nonblocking(data, bytes);
    if (bytes_read > 0) {
        signal_space();
    }
    return bytes_read;
}

/******************************************************************************
 * Condition variable handling
 ******************************************************************************/

void CircularBuffer::wait_for_space()
{
    /*
     *  wait_for_space() - Block until there is space to write to
     *
     *  If there is no space in the buffer, wait for a signal saying
     *  that someone read from the buffer.
     */
    pthread_mutex_lock(&cond_mutex_);
    while (!has_space()){
        pthread_cond_wait(&space_cond_, &cond_mutex_);
    }
    pthread_mutex_unlock(&cond_mutex_);
}

void CircularBuffer::wait_for_data()
{
    /*
     *  wait_for_data() - Block until there is data to read
     *
     *  If there is no data in the buffer, wait for a signal saying
     *  that someone write to the buffer.
     */
    pthread_mutex_lock(&cond_mutex_);
    while (!size()){
        pthread_cond_wait(&data_cond_, &cond_mutex_);
    }
    pthread_mutex_unlock(&cond_mutex_);
}

void CircularBuffer::signal_space()
{
    /*
     *  signal_space() - Send signal saying there is new space
     *
     *  Send signal telling any threads waiting on space to write to
     *  wake up.
     */
    pthread_mutex_lock(&cond_mutex_);
    pthread_cond_signal(&space_cond_);
    pthread_mutex_unlock(&cond_mutex_);
}

void CircularBuffer::signal_data()
{
    /*
     *  signal_data() - Send signal saying there is new data
     *
     *  Send signal telling any threads waiting on data to read to
     *  wake up.
     */
    pthread_mutex_lock(&cond_mutex_);
    pthread_cond_signal(&data_cond_);
    pthread_mutex_unlock(&cond_mutex_);
}
