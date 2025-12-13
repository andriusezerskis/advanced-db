# Load 
### 1. Nodes
    - 10k :
        - Load time [s]: 0.434 

    - 30k :
        - Load time [s]: 0.251

    - 1M :
        - Load time [s]: threshold reached with web version <:(

### 2. Edges
    - 30k :
        - Load time [s]: 0.551

    - 150k :
        - Load time [s]: 1.163

    - 3M :
        - Load time [s]: 

# Queries
### 1.  
    - 10k nodes / 30k edges : 
        - No cache : 12 ms
        - Cache : 4 ms

    - 30k nodes / 150k edges : 
        - No cache : 32 ms
        - Cache : 11 ms

    - 1M nodes / 3M edges : 
        - No cache : 
        - Cache : 

### 2.  
    - 10k nodes / 30k edges : 
        - No cache : 76 ms
        - Cache : 44 ms

    - 30k nodes / 150k edges : 
        - No cache : 177 ms
        - Cache : 144 ms

    - 1M nodes / 3M edges : 
        - No cache : 
        - Cache : 

### 3.
    - 10k nodes / 30k edges : 
        - No cache : 177ms huuuuuh
        - Cache : 17 ms

    - 30k nodes / 150k edges : 
        - No cache : 96 ms
        - Cache : 59 - 86 ms

    - 1M nodes / 3M edges : 
        - No cache : 
        - Cache : 

### 4.
    - 10k nodes / 30k edges : 
        - No cache : 14 ms
        - Cache : 3 ms

    - 30k nodes / 150k edges : 
        - No cache : 19 ms
        - Cache : 5 ms

    - 1M nodes / 3M edges : 
        - No cache : 
        - Cache : 

### 5. (Process : reload all collections then query 5 times. CLOSE with rate 0.4)

J'ai pas le machin pour random miskin

### 6. (Process : reload all collections then query 5 times. x 0.2 y 0.05)
    - 10k nodes / 30k edges : 
        - No cache : 37 ms
        - Cache : 5 ms decreasing to 1 ms (as there are less and less people to kill)

    - 30k nodes / 150k edges : 
        - No cache : 77 ms
        - Cache : 11 ms decreasing to 5ms after 5 attempts

    - 1M nodes / 3M edges : 
        - No cache : 
        - Cache : 
