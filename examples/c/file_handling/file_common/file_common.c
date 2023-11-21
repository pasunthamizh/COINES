#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/stat.h>
#include"coines.h"

#if defined(PC)
#include <dirent.h>
#endif

int list_files(int num_files) {
    coines_open_comm_intf(COINES_COMM_INTF_USB, NULL); //Wait here till USB is connnected
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

    coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
	
	return 0;
}

int get_file_size(char *filename) 
{
    struct stat st;
    coines_open_comm_intf(COINES_COMM_INTF_USB, NULL); //Wait here till serial port is opened

    if(stat(filename, &st) != 0)
    {
        printf("File doesn't exist - %s",filename);
        return -1;
    }
    printf("File size is %d bytes", (int)st.st_size);

    coines_close_comm_intf(COINES_COMM_INTF_USB, NULL);
	
	return 0;
}

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

int write_file(char *filename, char *input_string) {
   
	
   
    FILE *fp = fopen(filename,"w");
	
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

