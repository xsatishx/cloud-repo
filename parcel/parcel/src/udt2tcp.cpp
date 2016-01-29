/******************************************************************************
 *
 * FILE    : udt2tcp.cpp
 * PROJECT : parcel
 *
 * DESCRIPTION : This file contains functions for creating a UDT
 *               server that accpts incomming connections, creates a
 *               TCP connection to remote server, and proxies the
 *               traffic through.
 *
 * LICENSE : Licensed under the Apache License, Version 2.0 (the
 *           "License"); you may not use this file except in
 *           compliance with the License.  You may obtain a copy of
 *           the License at
 *
 *               http://www.apache.org/licenses/LICENSE-2.0
 *
 *           Unless required by applicable law or agreed to in
 *           writing, software distributed under the License is
 *           distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 *           CONDITIONS OF ANY KIND, either express or implied.  See
 *           the License for the specific language governing
 *           permissions and limitations under the License.)
 *
 ******************************************************************************/

#include "parcel.h"


EXTERN int udt2tcp_start(char *local_host, char *local_port,
                         char *remote_host, char *remote_port)
{
    /*
     *  udt2tcp_start() - starts a UDT proxy server
     *
     *  Starts a proxy server listening on local_host:local_port.
     *  Incomming connections get their own thread and a proxied
     *  connection to remote_host:remote_port.
     */

    int mss = MSS;
    int udt_buffer_size = BUFF_SIZE*2;
    int udp_buffer_size = BUFF_SIZE;

    return udt2tcp_start_configurable(local_host,
                                      local_port,
                                      remote_host,
                                      remote_port,
                                      mss,
                                      udt_buffer_size,
                                      udp_buffer_size);

}


EXTERN int udt2tcp_start_configurable(char *local_host,
                                      char *local_port,
                                      char *remote_host,
                                      char *remote_port,
                                      int mss,
                                      int udt_buffer_size,
                                      int udp_buffer_size)
{
    /*
     *  udt2tcp_start_configurable() - starts a configurable UDT proxy
     *  server
     *
     *  Starts a proxy server listening on local_host:local_port.
     *  Incomming connections get their own thread and a proxied
     *  connection to remote_host:remote_port.
     *
     *  mss             : maximum segment size
     *  udt_buffer_size : UDT buffer size in bytes
     *  udp_buffer_size : UDP buffer size in bytes
     *
     */
    log("Proxy binding to local UDT socket [%s:%s] to remote TCP [%s:%s]",
        local_host, local_port, remote_host, remote_port);
    debug("MSS            : %d", mss);
    debug("UDT_BUFFER_SIZE: %d", udt_buffer_size);
    debug("UDP_BUFFER_SIZE: %d", udp_buffer_size);

    addrinfo hints;
    addrinfo* res;
    int reuseaddr = 1;
    UDTSOCKET udt_socket;

    /*******************************************************************
     * Establish server socket
     ******************************************************************/

    /* Setup address information */
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_flags    = AI_PASSIVE;
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(NULL, local_port, &hints, &res) != 0){
        error("illegal port number or port is busy: [%s]", local_port);
        return -1;
    }

    /* Create the server socket */
    udt_socket = UDT::socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    UDT::setsockopt(udt_socket, 0, UDT_MSS, &mss, sizeof(int));
    UDT::setsockopt(udt_socket, 0, UDT_SNDBUF, &udt_buffer_size, sizeof(int));
    UDT::setsockopt(udt_socket, 0, UDP_SNDBUF, &udp_buffer_size, sizeof(int));
    UDT::setsockopt(udt_socket, 0, UDT_RCVBUF, &udt_buffer_size, sizeof(int));
    UDT::setsockopt(udt_socket, 0, UDP_RCVBUF, &udp_buffer_size, sizeof(int));
    UDT::setsockopt(udt_socket, 0, UDT_REUSEADDR, &reuseaddr, sizeof(int));

    /* Bind the server socket */
    if (UDT::bind(udt_socket, res->ai_addr, res->ai_addrlen) == UDT::ERROR){
        error("bind: %s", UDT::getlasterror().getErrorMessage());
        return -1;
    }
    log("Proxy bound to local UDT socket [%s:%s] to remote TCP [%s:%s]",
        local_host, local_port, remote_host, remote_port);

    /* We no longer need this address information */
    freeaddrinfo(res);

    /* Listen on the port for UDT connections */
    log("Calling UDT socket listen");
    if (UDT::listen(udt_socket, 10) == UDT::ERROR){
        error(": listen: %s", UDT::getlasterror().getErrorMessage());
        return -1;
    }

    log("Creating pipe2tcp server thread");
    pthread_t udt2tcp_server_thread;
    server_args_t *args = (server_args_t*) malloc(sizeof(server_args_t));
    args->remote_host = strdup(remote_host);
    args->remote_port = strdup(remote_port);
    args->udt_socket  = udt_socket;
    if (pthread_create(&udt2tcp_server_thread, NULL, udt2tcp_accept_clients, args)){
        error("unable to create udt2tcp server thread");
        free(args);
        return -1;
    }

    return 0;
}

EXTERN void *udt2tcp_accept_clients(void *_args_)
{
    /*
     *  udt2tcp_accept_clients() - Accepts incoming UDT clients
     *
     */
    server_args_t *args = (server_args_t*) _args_;

    while (1){
        /* Wait for the next connection */
        UDTSOCKET client_socket;
        sockaddr_storage clientaddr;
        int addrlen = sizeof(clientaddr);

        /* Wait for the next connection */
        debug("Accepting incoming UDT connections");
        if ((client_socket = UDT::accept(args->udt_socket, (sockaddr*)&clientaddr, &addrlen))
            == UDT::INVALID_SOCK){
            cerr << "accept: " << UDT::getlasterror().getErrorMessage() << endl;
            return 0;
        }
        log("New UDT connection");

        /* Create transcriber thread args */
        transcriber_args_t *transcriber_args = (transcriber_args_t *) malloc(sizeof(transcriber_args_t));
        transcriber_args->tcp_socket  = 0;  // will be set by thread_udt2tcp
        transcriber_args->udt_socket  = client_socket;
        transcriber_args->remote_host = args->remote_host;
        transcriber_args->remote_port = args->remote_port;

        /* Create tcp2udt thread */
        pthread_t tcp_thread;
        if (pthread_create(&tcp_thread, NULL, thread_tcp2udt, transcriber_args)){
            error("Unable to TCP thread");
            free(transcriber_args);
            return 0;
        } else {
            pthread_detach(tcp_thread);
        }

        /* Create udt2tcp thread */
        pthread_t udt_thread;
        if (pthread_create(&udt_thread, NULL, thread_udt2tcp, transcriber_args)){
            error("Unable to TCP thread");
            free(transcriber_args);
            return 0;
        } else {
            pthread_detach(udt_thread);
        }

    }

}

int connect_remote_tcp(udt2tcp_args_t *args)
{
    /*
     *  connect_remote_tct() - Creates client connection to tcp server
     *
     *  Connects a TCP socket to a remote tcp server.
     */
    debug("Connecting to remote UDT at [%s:%s]",
          args->remote_host, args->remote_port);

    struct addrinfo hints, *local, *peer;
    int tcp_socket;

    /* Create address information */
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_flags = AI_PASSIVE;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (0 != getaddrinfo(NULL, args->remote_port, &hints, &local)){
        error("incorrect network address");
        return -1;
    }

    /* Create the new socket */
    tcp_socket = socket(local->ai_family, local->ai_socktype, local->ai_protocol);
    freeaddrinfo(local);
    if (0 != getaddrinfo(args->remote_host, args->remote_port, &hints, &peer)){
        error("incorrect server/peer address: [%s:%s]",
              args->remote_host, args->remote_port);
        return -1;
    }

    /* Connect to the remote tcp server */
    if (connect(tcp_socket, peer->ai_addr, peer->ai_addrlen)){
        perror("TCP connect");
        return -1;
    }
    freeaddrinfo(peer);
    return tcp_socket;
}

void *thread_udt2tcp(void *_args_)
{
    /*
     *  thread_udt2tcp() -
     *
     */
    udt2tcp_args_t *args = (udt2tcp_args_t*) _args_;

    /*******************************************************************
     * Setup proxy procedure
     ******************************************************************/

    /*
     * I've made the design choice that the udt2tcp thread is not
     * responsible for the udt socket, because it is reading from it,
     * not writing.  Therefore, we will wait for an external entity to
     * set args->udt_socket to be a valid descriptor (it may already
     * be valid as set by a _start() method).
     */
    debug("Waiting on UDT socket ready");
    while (!args->udt_socket){
        // TODO: Add semaphore on socket ready, usleep is a
        // lazy solution for now
        usleep(100);
    }
    debug("UDT socket ready: %d", args->udt_socket);

    /*
     * Similarly I've made the design choice that the udt2tcp thread
     * IS responsible for the tcp socket, because it is writing to it,
     * not reading.  Therefore, we will attempt to connect to a remote
     * server via tcp. However, if there is already an existing tcp
     * connection, then by golly, someone wants us to use it (that
     * someone is me or you?).
     */
    if (!args->tcp_socket){
        if ((args->tcp_socket = connect_remote_tcp(args)) < 0){
            free(args);
            return NULL;
        }
    }

    /* Create udt2tcp pipe, read from 0, write to 1 */
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe");
        free(args);
        return NULL;
    }

    /*******************************************************************
     * Begin proxy procedure
     ******************************************************************/
    CircularBuffer *cbuffer = new CircularBuffer(CIRCULAR_BUFF_SIZE);

    /* Create UDT to pipe thread */
    pthread_t udt2pipe_thread;
    udt_pipe_args_t *udt2pipe_args = (udt_pipe_args_t*)malloc(sizeof(udt_pipe_args_t));
    udt2pipe_args->udt_socket = args->udt_socket;
    udt2pipe_args->pipe = cbuffer;
    debug("Creating udt2pipe thread");
    if (pthread_create(&udt2pipe_thread, NULL, udt2pipe, udt2pipe_args)){
        error("unable to create udt2pipe thread");
        free(args);
        return NULL;
    }

    /* Create pipe to TCP args */
    tcp_pipe_args_t *pipe2tcp_args = (tcp_pipe_args_t*)malloc(sizeof(tcp_pipe_args_t));
    pipe2tcp_args->tcp_socket = args->tcp_socket;
    pipe2tcp_args->pipe = cbuffer;
    debug("Calling pipe2tcp");
    pipe2tcp(pipe2tcp_args);  // There is no reason not to block on this now

    /* Join transcriber thread */
    void *ret;
    pthread_join(udt2pipe_thread, &ret);

    delete cbuffer;

    return NULL;
}
