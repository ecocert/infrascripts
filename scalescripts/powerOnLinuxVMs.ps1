param($start,$end) 
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!

for($num=$start; $num -le $end; $num++) {
      $vm = "Tiny-Linux-VM-$num"
      $vmInfo = Get-VM -Name $vm
      Start-VM -VM $vmInfo -Confirm:$false -RunAsync
      Write-Host -ForegroundColor GREEN " PoweredOn $vm"
}
      
 # now answer the Questions , we do this trick here after the loop
   # it takes few minuets for the VM to get power on and questions avalable
   
   Write-Host "Start sleeping 60 seconds"
   [Console]::Out.Flush() 
   Start-Sleep 60

   for($num=$start; $num -le $end; $num++) {
      $vm_ = Get-VM "Tiny-Linux-VM-$num"
     
      $ques_ = $vm_ | Get-VMQuestion
     
      if($ques_) {
        #Get-VM "Linux-VM$num" | Get-VMQuestion | Set-VMQuestion -Option "button.uuid.copiedTheVM" -Confirm:$false
        $ques_ | Set-VMQuestion -DefaultOption -Confirm:$false
        write-host "Answered question to the VM $vm_"
      }
   }
