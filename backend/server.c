#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include "llama.h"  // llama.cpp header

#define PORT 8000
#define BUFFER_SIZE 1024

// Structure to hold our model and context
typedef struct {
    struct llama_context* ctx;
    struct llama_model* model;
} llama_app;

// Initialize llama
llama_app* init_llama() {
    llama_app* app = malloc(sizeof(llama_app));
    
    // Initialize model
    struct llama_context_params params = llama_context_default_params();
    params.n_ctx = 2048;
    params.n_threads = 4;
    params.seed = -1;
    
    // Load model
    const char* model_path = "../models/Llama-3.2-1B-Instruct-Q3_K_L.gguf";
    app->model = llama_load_model_from_file(model_path, params);
    if (!app->model) {
        fprintf(stderr, "Failed to load model\n");
        free(app);
        return NULL;
    }
    
    // Create context
    app->ctx = llama_new_context_with_model(app->model, params);
    if (!app->ctx) {
        fprintf(stderr, "Failed to create context\n");
        llama_free_model(app->model);
        free(app);
        return NULL;
    }
    
    return app;
}

// Handle streaming request
void handle_stream_request(int client_socket, llama_app* app, const char* prompt) {
    // SSE headers
    const char* headers = "HTTP/1.1 200 OK\r\n"
                         "Content-Type: text/event-stream\r\n"
                         "Cache-Control: no-cache\r\n"
                         "Connection: keep-alive\r\n"
                         "Access-Control-Allow-Origin: *\r\n\r\n";
    write(client_socket, headers, strlen(headers));
    
    // Tokenize input
    llama_token tokens[1024];
    int n_tokens = llama_tokenize(app->ctx, prompt, strlen(prompt), tokens, 1024, true);
    
    if (n_tokens < 0) {
        const char* error = "data: {\"error\": \"Tokenization failed\"}\n\n";
        write(client_socket, error, strlen(error));
        return;
    }
    
    // Generate tokens
    for (int i = 0; i < n_tokens; i++) {
        // Decode next token
        if (llama_decode(app->ctx, tokens, n_tokens) != 0) {
            break;
        }
        
        // Get logits
        float* logits = llama_get_logits(app->ctx);
        if (!logits) {
            break;
        }
        
        // Get token text
        const char* token_text = llama_token_get_text(app->ctx, tokens[i]);
        if (!token_text) {
            break;
        }
        
        // Format SSE message
        char message[1024];
        snprintf(message, sizeof(message), 
                "data: {\"text\": \"%s\", \"probabilities\": {\"eos\": %f}}\n\n",
                token_text, logits[0]);
        write(client_socket, message, strlen(message));
    }
    
    // Send done event
    const char* done = "data: {\"finish\": true}\n\n";
    write(client_socket, done, strlen(done));
}

int main() {
    // Initialize llama
    llama_app* app = init_llama();
    if (!app) {
        return 1;
    }
    
    // Create socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        fprintf(stderr, "Failed to create socket\n");
        return 1;
    }
    
    // Set up server address
    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    // Bind socket
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        fprintf(stderr, "Failed to bind socket\n");
        return 1;
    }
    
    // Listen for connections
    if (listen(server_fd, 3) < 0) {
        fprintf(stderr, "Failed to listen\n");
        return 1;
    }
    
    printf("Server running on port %d\n", PORT);
    
    while (1) {
        // Accept connection
        int client_socket = accept(server_fd, NULL, NULL);
        if (client_socket < 0) {
            fprintf(stderr, "Failed to accept connection\n");
            continue;
        }
        
        // Read request
        char buffer[BUFFER_SIZE] = {0};
        read(client_socket, buffer, BUFFER_SIZE);
        
        // Parse request (very basic parsing)
        if (strstr(buffer, "GET /stream") != NULL) {
            // Extract prompt from query string (basic implementation)
            char* prompt = strstr(buffer, "context=");
            if (prompt) {
                prompt += 8;  // Skip "context="
                char* end = strchr(prompt, ' ');
                if (end) *end = '\0';
                
                handle_stream_request(client_socket, app, prompt);
            }
        }
        
        close(client_socket);
    }
    
    // Cleanup
    llama_free(app->ctx);
    llama_free_model(app->model);
    free(app);
    close(server_fd);
    
    return 0;
} 