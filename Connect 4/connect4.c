//You can include any of headers defined in the C11 standard here. They are:
//assert.h, complex.h, ctype.h, errno.h, fenv.h, float.h, inttypes.h, iso646.h, limits.h, locale.h, math.h, setjmp.h, signal.h, stdalign.h, stdarg.h, stdatomic.h, stdbool.h, stddef.h, stdint.h, stdio.h, stdlib.h, stdnoreturn.h, string.h, tgmath.h, threads.h, time.h, uchar.h, wchar.h or wctype.h
//You may not include any other headers.

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdbool.h>
#include<ctype.h>
#include"connect4.h"

int gravity(int currentCol, board u);
void capitaliseWinner(int i, int j, char direction, board u);
board copyBoard(board c);


struct board_structure {
/*Put something suitable here*/
char **boardArray;
int numRows;
int numCols;
char nextPlayer;

};

board setup_board(){
//You may put code here
  board newBoard = malloc(sizeof(struct board_structure));
  if(newBoard == NULL){
    fprintf(stderr, "Failed to allocate required memory");
    exit(1);
  }
  
  newBoard->nextPlayer = 'z';
  return newBoard;
}

void cleanup_board(board u){
//You may put code here
  for(int i = 0; i< u->numRows; i++){
    free(u->boardArray[i]);
  }
  free(u->boardArray);
  free(u);
}

void read_in_file(FILE *infile, board u){
//You may put code here
  char c;
  int countLines = 0;
  int countChars = 0;
  int xCount = 0;
  int oCount = 0;
  char *currentRow = malloc(sizeof(char));
  if(currentRow == NULL){
    fprintf(stderr,"Failed to allocate required memory");
    cleanup_board(u);
    exit(1);
  }
  u->boardArray = malloc(sizeof(char));

  char c1 = fgetc(infile);
  if(c1 == EOF){
    fprintf(stderr,"File is empty");
    exit(1);
  }else{
    ungetc(c1,infile);
  }

  for (c = getc(infile); c != EOF; c = getc(infile)){
    if(c != 'x' && c != 'o' && c != '.' && c != '\n'){
        fprintf(stderr,"File contained invalid characters");
        cleanup_board(u);
        exit(1);
       }

      if(c == 'x'){
        xCount++;
      }else if(c == 'o'){
        oCount++;
      }
      if (countLines == 0){
        u->numCols = countChars;
      }
      if (c == '\n'){
          countLines = countLines + 1;
          u->boardArray = realloc(u->boardArray, countLines * sizeof(currentRow));
          u->boardArray[countLines -1] = malloc(countChars * sizeof(char));
          if(u->boardArray[countLines-1] == NULL){
            fprintf(stderr, "Failed to allocate required memory");
            cleanup_board(u);
            exit(1);
          }
          strcpy(u->boardArray[countLines -1], currentRow);

          countChars = 0;
      }
      else{  
          countChars++;
          if (countLines == 0){
            currentRow = realloc(currentRow, countChars * sizeof(char));     
          } 
          currentRow[countChars - 1] = c;
          
        }        
  }
  free(currentRow);
  u->numRows = countLines;
  

  if(oCount < xCount){
    u->nextPlayer = 'x';
  }else{
    u->nextPlayer = 'o';
  }
  

}

void write_out_file(FILE *outfile, board u){
//You may put code here
  if(outfile == NULL){
    fprintf(stderr,"Error opening file");
    cleanup_board(u);
    exit(1);
  }
  for(int i = 0; i < u->numRows; i++){
    fprintf(outfile, "%s\n", u->boardArray[i]);
  }
}

char next_player(board u){
//You may put code here
    if(u->nextPlayer =='x'){
      return 'o';
    }else{
      return 'x';
    } 
}

char current_winner(board u){
//You may put code here
  bool xWin = false;
  bool oWin = false;
  bool notFull = false;

  for(int i = 0;i < u->numCols; i++){
    if(u->boardArray[0][i] == '.'){
      notFull = true;
    }
  }
  
  for(int i = 0; i < u->numRows; i++){
    for(int j = 0; j < u->numCols; j++){
      //Horizontal Check
      if(((u->boardArray[i][j%(u->numCols)] == u->boardArray[i][(j+1)%(u->numCols)]) && (u->boardArray[i][j%(u->numCols)]== u->boardArray[i][(j+2)%(u->numCols)]) && (u->boardArray[i][j%(u->numCols)]== u->boardArray[i][(j+3)%(u->numCols)])) && u->boardArray[i][j] != '.'){
        if(((u->boardArray[i][j%(u->numCols)] == 'x') && xWin == false) || ((u->boardArray[i][j%(u->numCols)] == 'o') && oWin == false)){
          
          if(u->boardArray[i][j%(u->numCols)] == 'x'){
            xWin = true;
          }else{
            oWin = true;
          }
          capitaliseWinner(i, j, 'h', u);
        }
      }
      //Vertical Check
      else if(((u->boardArray[i%u->numRows][j] == u->boardArray[(i+1)%u->numRows][j]) && (u->boardArray[i%u->numRows][j]== u->boardArray[(i+2)%u->numRows][j]) && (u->boardArray[i%u->numRows][j] == u->boardArray[(i+3)%u->numRows][j])) && u->boardArray[i%u->numRows][j] != '.'){
        if((i+3) < u->numRows){
          if((u->boardArray[i%u->numRows][j] == 'x' && xWin == false) || (u->boardArray[i%u->numRows][j] == 'o' && oWin == false)){
            
            if(u->boardArray[i][j] == 'x'){
            xWin = true;
            }else{
              oWin = true;
            }
            capitaliseWinner(i, j, 'v', u);
          }
          
        }
      }
      //Right Diagonal Check
      else if(((u->boardArray[i%u->numRows][j%u->numCols] == u->boardArray[(i+1)%u->numRows][(j+1)%u->numCols]) && (u->boardArray[i%u->numRows][j]== u->boardArray[(i+2)%u->numRows][(j+2)%u->numCols]) && (u->boardArray[i%u->numRows][j] == u->boardArray[(i+3)%u->numRows][(j+3)%u->numCols])) && u->boardArray[i%u->numRows][j] != '.'){
        if(i+3 < u->numRows){
          if((u->boardArray[i%u->numRows][j%(u->numCols)] == 'x' && xWin == false) || (u->boardArray[i%u->numRows][j%(u->numCols)] == 'o' && oWin == false)){
            
            if(u->boardArray[i][j] == 'x'){
            xWin = true;
          }else{
            oWin = true;
          }
          capitaliseWinner(i, j, 'r', u);
          }      
        }
      }
      // Left Diagonal Check
      else if(((u->boardArray[i%u->numRows][j%u->numCols] == u->boardArray[(i+1)%u->numRows][(j-1)%u->numCols]) && (u->boardArray[i%u->numRows][j]== u->boardArray[(i+2)%u->numRows][(j-2)%u->numCols]) && (u->boardArray[i%u->numRows][j] == u->boardArray[(i+3)%u->numRows][(j-3)%u->numCols])) && u->boardArray[i%u->numRows][j] != '.'){
        if(i+3 < u->numRows){
          if((u->boardArray[i%u->numRows][j%(u->numCols)] == 'x' && xWin == false) || (u->boardArray[i%u->numRows][j%(u->numCols)] == 'o' && oWin == false)){
            
            if(u->boardArray[i][j] == 'x'){
            xWin = true;
          }else{
            oWin = true;
          }
          capitaliseWinner(i,j,'l',u);
          }
          
        }
      }
    }
  }

  if((xWin && oWin) == true || notFull == false){
    return 'd';
  } else if(xWin == true){
    return 'x';
  }else if(oWin == true){
    return 'o';
  }else{
    return '.';
  }
  

}

struct move read_in_move(board u){
//You may put code here
  
  struct move newMove;  
 
  
  printf("Player %c enter column to place your token: ",next_player(u)); //Do not edit this line
  scanf("%d", &newMove.column);

  printf("Player %c enter row to rotate: ",next_player(u)); // Do not edit this line
  scanf("%d", &newMove.row);

 
  is_valid_move(newMove, u);
    
  
  return newMove;
}

int is_valid_move(struct move m, board u){
//You may put code here
  

  if(abs(m.row) > u->numRows){
    fprintf(stderr,"Row selection not in range\n");
    return 0;
  }
  else if(m.column > u->numCols || m.column < 1){
    fprintf(stderr,"Column Selection Not in Range\n");
    return 0;
  }
  else if (u->boardArray[0][m.column -1] != '.'){
    fprintf(stderr,"Selected Column is Full\n");
    return 0;

  }else{
    return 1;
  }
}

char is_winning_move(struct move m, board u){
//You may put code here
  
  board boardCopy = copyBoard(u);
  
  play_move(m, boardCopy);
  char result = current_winner(boardCopy);
  cleanup_board(boardCopy);

  return result;
    
}


void play_move(struct move m, board u){
//You may put code here
int temp, i;
char currentToken;


u->boardArray[gravity(m.column - 1, u)][m.column - 1] = next_player(u);
u->nextPlayer = next_player(u);

if(m.row != 0){
  if (m.row > 0){
    m.row = u->numRows - abs(m.row) + 1;
    temp = u->boardArray[m.row-1][u->numCols - 1];
    for (i = u->numCols - 1; i > 0; i--){
      u->boardArray[m.row-1][i] = u->boardArray[m.row-1][i-1];
    }
    u->boardArray[m.row-1][0] = temp;

}
  else if(m.row < 0){
    m.row = (u->numRows - abs(m.row) + 1);
    temp = u->boardArray[m.row-1][0];
    for (i = 0; i < u->numCols; i++){
      u->boardArray[m.row-1][i] = u->boardArray[m.row-1][i+1];
    }
    u->boardArray[m.row-1][u->numCols - 1] = temp;


}
  for (i = 0; i < u->numCols; i++){
    if(u->boardArray[m.row - 1][i] != '.'){
      currentToken = u->boardArray[m.row - 1][i];
      u->boardArray[m.row - 1][i] = '.';
      u->boardArray[gravity(i, u)][i] = currentToken;

    }
  for (int j = m.row-2; j>=0; j--){
    if(u->boardArray[j][i] !='.'){
      currentToken = u->boardArray[j][i];
      u->boardArray[j][i] = '.';
      u->boardArray[gravity(i,u)][i] = currentToken; 
    }
  }
  
}
}
current_winner(u);
}

// //You may put additional functions here if you wish.
int gravity(int currentCol, board u){
  int i;
  for(i = u->numRows - 1; i >= 0; i--){
    if (u->boardArray[i][currentCol] == '.'){
      break;
    }
  }
  return i;
}

void capitaliseWinner(int i, int j, char direction, board u){
  switch(direction){
    case 'h':
      u->boardArray[i][j%(u->numCols)] = u->boardArray[i][(j+1)%(u->numCols)] = u->boardArray[i][(j+2)%(u->numCols)] = u->boardArray[i][(j+3)%(u->numCols)] = toupper(u->boardArray[i][j]);
      break;
    case 'v':
      u->boardArray[i%u->numRows][j] = u->boardArray[(i+1)%u->numRows][j] = u->boardArray[(i+2)%u->numRows][j] = u->boardArray[(i+3)%u->numRows][j] = toupper(u->boardArray[i%u->numRows][j]);
      break;
    case 'r':
      u->boardArray[i%u->numRows][j%u->numCols] = u->boardArray[(i+1)%u->numRows][(j+1)%u->numCols] = u->boardArray[(i+2)%u->numRows][(j+2)%u->numCols] = u->boardArray[(i+3)%u->numRows][(j+3)%u->numCols] = toupper(u->boardArray[i%u->numRows][j%u->numCols]);
      break;
    case 'l':
      u->boardArray[i%u->numRows][j%u->numCols] = u->boardArray[(i+1)%u->numRows][(j-1)%u->numCols] = u->boardArray[(i+2)%u->numRows][(j-2)%u->numCols] = u->boardArray[(i+3)%u->numRows][(j-3)%u->numCols] = toupper(u->boardArray[i%u->numRows][j%u->numCols]);
      break;
  }
}

board copyBoard(board c){
  board boardCopy = malloc(sizeof(struct board_structure));
  boardCopy->numCols = c->numCols;
  boardCopy->numRows = c->numRows;
  boardCopy->boardArray = malloc(sizeof(char*) * boardCopy->numRows);
  if(boardCopy->boardArray == NULL){
    fprintf(stderr,"Failed to allocate required memory");
    cleanup_board(boardCopy);
    cleanup_board(c);
    exit(1);
  }

  for(int i = 0; i < boardCopy->numRows; i++){
    boardCopy->boardArray[i] = malloc(sizeof(char) * (boardCopy->numCols + 1));
    if(boardCopy->boardArray[i] == NULL){
      fprintf(stderr,"Failed to allocate required memory");
      cleanup_board(boardCopy);
      cleanup_board(c);
      exit(1);
    }
    strcpy(boardCopy->boardArray[i], c->boardArray[i]);
  }

  return boardCopy;
}



