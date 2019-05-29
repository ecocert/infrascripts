 
##### Script Starts Here ######  
 For ( $num=1;$num -le 25;$num++) {
 
        if (test-Connection -ComputerName esx-horizontal-$num.corp.local -Count 2 -Quiet ) {  
         
            write-Host "esx-horizontal-$num.corp.local is alive and Pinging " -ForegroundColor Green
            connect-viserver -server esx-horizontal-$num.corp.local -User root -Password VMware1! 
            Set-VMHost -VMHost esx-horizontal-$num.corp.local -LicenseKey NH684-VY5D6-W8X8T-0V3HM-1WYM0 -State Connected

        } else 
                     
        { Write-Warning "esx-horizontal-$num.corp.local is not up, please check after sometime" 
             
        }     
        if (test-Connection -ComputerName esx-horizontal-$num-1.corp.local -Count 2 -Quiet ) {  
         
            write-Host "esx-horizontal-$num-1.corp.local is alive and Pinging " -ForegroundColor Green 
            connect-viserver -server esx-horizontal-$num-1.corp.local -User root -Password VMware1!
            Set-VMHost -VMHost esx-horizontal-$num-1.corp.local -LicenseKey NH684-VY5D6-W8X8T-0V3HM-1WYM0 -State Connected
         
        } else 
                     
        { Write-Warning "esx-horizontal-$num-1.corp.local is not up, please check after sometime" 
             
        }   
         
} 

