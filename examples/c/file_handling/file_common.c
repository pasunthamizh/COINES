/**
 * 
 *
 * 
 * @file    file_common.c
 * @brief 	List the number of files mentioned by the user
 *			Get the size of file mentioned by the user
 *			Read the content in the file with limits given by user
 *			Write the content to the file given by the user 
 *			append the conntent to the file as given by the user 
 *			delete the file given by the user 
 *			
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/stat.h>
#include"coines.h"

#if defined(PC)
#include <dirent.h>
#endif

/************************************************************
Function name: list_files 
Function Description:  To List number of files as per user input
Inputs   :  number of files to list in dirrectory
Outputs  :  Lists selected number of files in command prompt
************************************************************/

int list_files(int num_files) {
  
	DIR *d;
    struct dirent *dir;
	int i=0 ;
    d = opendir(".");
	if(num_files <= 0)
    {
        printf("Number of Files to list is invalid");
        return -1;
    }	
	
    if (d)
    {
        while ((dir = readdir(d)) != NULL  )
        {
			 if(i>=2 && num_files )
			{
				printf("%s\n", dir->d_name);   
			    num_files--;
			 }
			 i++;
			 
		}
	
        closedir(d);
    }

  
	return 0;
}

/***************************************************************
Function name       : get_file_size
Function Description: To read the size of the file given by user
Inputs 				: File name 
Outputs 			: size of file in integer
***************************************************************/
int get_file_size(char *filename) 
{
    struct stat st;
  
    if(stat(filename, &st) != 0)
    {
        printf("File doesn't exist - %s",filename);
        return -1;
    }
    printf("File size is %d bytes", (int)st.st_size);

   	return 0;
}

/****************************************************************
Function name       : read_file
Function Description: Read the content in the file given by user  
Inputs              : Filename and number of characters to read 
Outputs             : display content in the command prompt
****************************************************************/
int read_file(char *filename, int num_chars) {
	struct stat st;
    char a;
    int num_chars_temp =num_chars ;
    
    FILE *fp = fopen(filename,"r");
    if(stat(filename, &st) != 0)
    {
        printf("File doesn't exist - %s",filename);
        return -1;
    }	
	if(num_chars <= 0)
    {
        printf("Number of characters to read is invalid");
        return -1;
    }	
    while(num_chars_temp-- )
    {
        a= fgetc(fp);
        printf("%c",a);
		if(a== EOF)
		{
			printf("\n Number of characters to print is %d ",num_chars - num_chars_temp - 1);
			break;
		}
			
    } 	
    
    fflush(stdout);
    fclose(fp);
      
	return 0;
}
/************************************************************************
Function name		: write_file
Function Description: Write user input string to the user given filename
Inputs 				: File name and input string 
Outputs				: Write data to file
************************************************************************/
int write_file(char *filename, char *input_string) {
   
	
   
   
	
	if(*input_string == '\0')
	{ 
		printf("Cannot write NULL data to file ");
		return -1;
		
	}
	FILE *fp = fopen(filename,"w");
    
	fprintf(fp,"%s",input_string); 
    
    fclose(fp);
	
	printf("Writing to file %s...\n", filename);
	
	return 0;
}

/**************************************************************************************
Function name		: append_to_file
Function Description: Append user input to already present file or will create the file 
Inputs 				: File name and input string 
Outputs 			: Write data to file
**************************************************************************************/
int append_to_file(char *filename, char *input_string) {
   
	
   
    
	struct stat st;
   
   if((stat(filename, &st) != 0) && (*input_string != '\0'))
    {
        printf("File doesn't exist - %s\n",filename);
		printf("Creating a new file - %s\n",filename);
		
    }
	FILE *fp = fopen(filename,"a");
	if(*input_string == '\0')
	{ 
		printf("Cannot write NULL data to file ");
		return -1;
		
	}

    
	fprintf(fp,"%s",input_string); 
    
    fclose(fp);
	
	printf("Writing to file %s...\n", filename);
	
	return 0;
}
/******************************************************
Function name		: remove_file
Function Description: delete the file given by the user
Inputs 				: File name 
Outputs 			: given file will be deleted.
*******************************************************/
int remove_file(char *filename) {
   
	
   struct stat st;
    if(stat(filename, &st) != 0)
    {
        printf("File doesn't exist - %s",filename);
        return -1;
    }
	
	remove(filename);
  
	
	return 0;
}

/***********************************************************************
Function name: Main
Function Description:  Receive data from command prompt and 
						file handling will be done as per the arguments  
***********************************************************************/
int main(int argc, char *argv[]) {
	
	  if (argc < 2) {
        printf("Usage: %s <options>\n", argv[0]);
        return 1;
    }
	coines_open_comm_intf(COINES_COMM_INTF_USB, NULL); //Wait here till serial port is opened
  
    char option = argv[1][1]; // Assuming options are single letters
    switch (option) {
        case 'l':
            if (argc < 3) {
                printf("Missing argument for -l option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
            list_files(atoi(argv[2]));
            break;
        case 's':
            if (argc < 3) {
                printf("Missing argument for -s option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
            get_file_size(argv[2]);
            break;
        case 'r':
            if (argc < 4) {
                printf("Missing arguments for -r option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
            read_file(argv[2], atoi(argv[3]));
            break;
        case 'w':
            if (argc < 4) {
                printf("Missing arguments for -w option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
            write_file(argv[2], argv[3]);
            break;
        case 'd':
            if (argc < 3) {
                printf("Missing arguments for -d option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
             remove_file(argv[2]);
            break;
			
		case 'a':
            if (argc < 4) {
                printf("Missing arguments for -w option\n");
				coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
                return 1;
            }
            append_to_file(argv[2], argv[3]);
            break;
        default:
            printf("Invalid option\n");
			coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
            return 1;
    }
	coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
    return 0;
}

