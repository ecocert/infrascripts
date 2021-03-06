param($start,$end) 
#####################################################################
# Load VMware Plugins and connect to vCenter
#####################################################################
 
Add-PSSnapin vmware.vimautomation.core
## Enter your vCenter here
connect-viserver -server vcsa-02a.corp.local -User administrator@corp.local -Password VMware1!
 
########################################################################
# Add Multiple Hosts to vCenter
######################################################################## 

 $waittime = "60"
 $clusters = Get-Cluster
 
 
if( !($clusters -like "ScaleCluster1") )
{
    New-Cluster -Name "ScaleCluster1" -Location "Cert-DC" -DRSEnabled -DRSMode Manual
}
if( !($clusters -like  "ScaleCluster2") )
{
    New-Cluster -Name "ScaleCluster2" -Location "Cert-DC" -DRSEnabled -DRSMode Manual
}
if( !($clusters -like "ScaleCluster3") )
{
    New-Cluster -Name "ScaleCluster3" -Location "Cert-DC" -DRSEnabled -DRSMode Manual
}
if( !($clusters -like "ScaleCluster4") )
{
    New-Cluster -Name "ScaleCluster4" -Location "Cert-DC" -DRSEnabled -DRSMode Manual
}
 
 Function GetCluster()
 {
    param($number)
    
    switch ($number)
     {

        {1..50 -contains $_}
        {
          "ScaleCluster1";break;
        }
        {51..100 -contains $_}
        {
          "ScaleCluster2";break;
        }
        {101..150 -contains $_}
        {
          "ScaleCluster3";break;
        }
        {151..200 -contains $_}
        {
          "ScaleCluster4";break;
        }
    }
 }


 For ( $num=$start;$num -le $end;$num++) {
 $ESXiLocation = GetCluster -number ($num)  
 Add-VMHost -Name esx-scale-$num -Location  $ESXiLocation -User root -Password VMware1! -RunAsync -force 
 Write-Host -ForegroundColor GREEN "Adding ESXi host esx-scale-$num to vCenter in cluster $ESXiLocation" 
  
}  

Write "waiting for $waittime seconds for the completion of adding hosts"
Start-Sleep -Seconds $waittime;

For ( $num=$start;$num -le $end;$num++) {
 
 Set-VMHost -VMHost esx-scale-$num.corp.local -LicenseKey NH684-VY5D6-W8X8T-0V3HM-1WYM0 -State Connected
 
 Write-Host -ForegroundColor GREEN "Setting License done to host esx-scale-$num"  
 
}  

Disconnect-VIServer -server vcsa-02a.corp.local -confirm:$false