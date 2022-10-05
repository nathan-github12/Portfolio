#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdbool.h>
#include<locale.h>



int compareInt(const void *a, const void *b){
    const char **aa = (const char **)a;
    const char **bb = (const char **)b;
    char *ptr;

    int p1 = strtol(*aa, &ptr, 10);
    int p2 = strtol(*bb, &ptr, 10);

    return (p1 > p2) - (p1 < p2);
}

int compareStr(const void *a, const void *b){
    const char **aa = (const char **)a;
    const char **bb = (const char **)b;


    return strcoll(*aa,*bb);
}

int compareInt_r(const void *a, const void *b){
    return (compareInt(a,b))*-1;
}

int compareStr_r(const void *a, const void *b){
    return (compareStr(a,b))*-1;
}

int main(int argc, char**argv){
    
   
    bool output = false;
    bool numeric = false;
    bool reverse = false;
    bool help = false;

    for (int i = 1; i < argc; i++){
        if(argv[i][0] == '-'){
            for (int j = 1; j < strlen(argv[i]); j++){
                switch(argv[i][j]){
                    case 'o':
                        output = true;
                        break;
    
                    case 'n':
                        numeric = true;
                        break;

                    case 'r':
                        reverse = true;
                        break;

                    case 'h':
                        printf("\n NAME\n \t sort - sort lines of text files \n SYNOPSIS\n\tsort [OPTION]... [FILE]...\n\tsort [OPTION]... --files0-from=F\n DESCRIPTION\n -n, --numeric-sort \n \tcompare according to string numerical value\n -r, --reverse\n \treverse the result of comparisons\n -o, --output=FILE \n \twrite result to FILE instead of standard output\n");
                        help = true;
                        break;
                    
                    default:
                        printf("Invalid input\n");                    
                }
            }
        }
    }




    FILE *inpFile;
    FILE *outFile;

    char *out_file;
    char **input_file = malloc(sizeof(char*));
    if(input_file == NULL){
        fprintf(stderr,"Failed to allocate required memory");
        exit(1);
    }
    int inputFiles = 0;

    for(int i = 1; i < argc; i++){
        if(argv[i][0] != '-'){
            for(int j =1; j < strlen(argv[i-1]); j++){
                if(argv[i-1][j]=='o' && argv[i-1][0]=='-'){
                    out_file = argv[i];
                    
                }else{
                    inputFiles++;
                    input_file = realloc(input_file, inputFiles*sizeof(char*));
                    input_file[inputFiles -1] = malloc(strlen(argv[i])*sizeof(char*));
                    if(input_file[inputFiles-1] == NULL){
                        fprintf(stderr,"Failed to allocate required memory");
                        exit(1);
                    }
                    input_file[inputFiles -1] = argv[i];
                    break;
                    
  
                }
            }   
        }
    }

    
    int lineSize = 200;
    char *currentLine = malloc(lineSize*sizeof(char));
    if(currentLine == NULL){
        fprintf(stderr,"Failed to allocate required memory");
        exit(1);
    }
    char **fileContents = malloc(sizeof(char*));
    if(fileContents == NULL){
        fprintf(stderr,"Failed to allocate required memory");
        exit(1);
    }
    int tempSize;
    int numLines = 0;
    
    
    if(inputFiles == 0){
            inpFile = stdin;
            inputFiles = 1;
    }

    for(int i = 0; i < inputFiles; i++){
        
        if(inpFile != stdin){
            inpFile = fopen(input_file[i], "r");
        } 
         while(fgets(currentLine,lineSize,inpFile)!=NULL) {
        numLines++;
        tempSize = strlen(currentLine);
        fileContents = realloc(fileContents, sizeof(char*)*numLines);

        fileContents[numLines -1] = malloc(tempSize*sizeof(char));
        if(fileContents[numLines-1] == NULL){
        fprintf(stderr,"Failed to allocate required memory");
        exit(1);
    }
        if (currentLine[tempSize-1] == '\n') {
            currentLine[tempSize-1] = '\0';
        }
        strcpy(fileContents[numLines-1],currentLine);
        free(currentLine);
        currentLine = malloc(lineSize*sizeof(char));
        if(currentLine == NULL){
        fprintf(stderr,"Failed to allocate required memory");
        exit(1);
    }
    }
    fclose(inpFile);
}
    

    
    setlocale(LC_ALL,"en_GB.UTF-8");

    if (numeric == true && reverse == true){
        qsort(fileContents, numLines, sizeof(char*), compareInt_r);
    }else if(numeric == true){
        qsort(fileContents, numLines, sizeof(char*), compareInt);
    }else if(reverse == true){
        qsort(fileContents, numLines, sizeof(char*), compareStr_r);
    }else{
        qsort(fileContents, numLines, sizeof(char*), compareStr);    
        }
    setlocale(LC_ALL,NULL);


    if(output == false){
        for(int i = 0; i<numLines;i++){
            fputs(fileContents[i], stdout);
            fputs("\n", stdout);
        }
        
    }else{
        outFile = fopen(out_file, "w");
        if(outFile == NULL){
            fprintf(stderr, "Error opening file");
            exit(1);
        }
        for(int i = 0; i < numLines; i++){
            fputs(fileContents[i], outFile);
            fputs("\n", outFile);
        }
        
    }
    return 0;
}