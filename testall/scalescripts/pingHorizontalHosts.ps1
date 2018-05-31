 
##### Script Starts Here ######  
 For ( $num=1;$num -le 32;$num++) {
 
        if (test-Connection -ComputerName esx-horizontal-$num.corp.local -Count 2 -Quiet ) {  
         
            write-Host "esx-horizontal-$num.corp.local is alive and Pinging " -ForegroundColor Green 
         
        } else 
                     
        { Write-Warning "esx-horizontal-$num.corp.local is not up, please check after sometime" 
             
        }     
        if (test-Connection -ComputerName esx-horizontal-$num-1.corp.local -Count 2 -Quiet ) {  
         
            write-Host "esx-horizontal-$num-1.corp.local is alive and Pinging " -ForegroundColor Green 
         
        } else 
                     
        { Write-Warning "esx-horizontal-$num-1.corp.local is not up, please check after sometime" 
             
        }   
         
} 

