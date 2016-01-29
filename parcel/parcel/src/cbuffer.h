/*
 * File taken from
 * http://www.asawicki.info/news_1468_circular_buffer_of_raw_binary_data_in_c.html
 * and modified to be thread safe for posix systems and to block on write.
 */

#ifndef __CBUFFER_H__
#define __CBUFFER_H__

#include <unistd.h>
#include <cstdlib>
#include <pthread.h>
#include <cstring>
#include <cstdio>
#include <algorithm>

class CircularBuffer
{
public:
    CircularBuffer(size_t capacity);
    ~CircularBuffer();

    /* True if there is space is available to write to */
    bool has_space () const { return (capacity_ - size_ > 1); }
    /* How many bytes are currently in the buffer */
    size_t size () const { return size_;     }
    /* Total capacity */
    size_t capacity () const { return capacity_; }
    /* Close the buffer */
    void close () { closed_ = true;   }
    /* Return number of bytes read. */
    size_t read_nonblocking(char *data, size_t bytes);
    /* Return number of bytes written. */
    size_t write_nonblocking(const char *data, size_t bytes);
    /* Return number of bytes written. */
    size_t write(const char *data, size_t bytes);
    /* Return number of bytes read. */
    size_t read(char *data, size_t bytes);
    /* Wait until there is space to write */
    void wait_for_space();
    /* Wait until there is data to read */
    void wait_for_data();
    /* Signal that there is space to write */
    void signal_space();
    /* Signal that there is data to read */
    void signal_data();

private:
    size_t beg_index_, end_index_, size_, capacity_;
    pthread_cond_t space_cond_, data_cond_;
    pthread_mutex_t cond_mutex_, pointer_mutex_;
    bool closed_;
    char *data_;
};

#endif //__CBUFFER_H__
