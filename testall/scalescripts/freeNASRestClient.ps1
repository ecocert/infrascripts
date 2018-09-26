param([Int32]$index, [Int32]$action)


$server = "192.168.110.6"+$index
write-host "Creating Storage volume, extent and target to extent in the FREENAS Server $server" -ForegroundColor magenta

$uri = "http://$server"
$diskSizeInGB = 1024*1024*1024


$user = "root"
$pass = "VMware1!"
$pair = "${user}:${pass}"

$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)

$basicAuthValue = "Basic $base64"
$headers = @{Authorization = $basicAuthValue;Accept='application/json'}

$global_extentID = 0
$global_storageVolumeName = ""



<#-----FUNCTION TO GET DISK RESOURCE FROM FREENAS SERVER-----#>
Function getDISKResource()
{
    
    $getDiskURI = $uri+"/api/v1.0/storage/disk/"
    Write-Debug "getDiskURI is $getDiskURI"
    # Submit the request to the RESTful Resource using the GET method
    try 
    {
        #First Get the diskName and diskSize of the new disk addded to the storage VM
        $response = Invoke-WebRequest -Uri $getDiskURI  -Headers $headers -Method Get

        $status = [int]$response.StatusCode
        Write-Debug "Response status code returned by getDISKResource is $Status"

        if ($status -ne '200'){
            Write-Error "Error in retrieving the disk resource"
            return $false
        }
        Write-Debug "Response from getDISKResource is $response.Content"
        $result = $response.Content | ConvertFrom-Json


        write-Host "Length of disk array returned by getDISKResource is "$result.Length
        

        if($result.Length -eq 0) 
        {
            Write-warning "There is no new disk added to the FREENAS Server $server"
            return $false
        }
        
        $diskSize = $result[$result.Length-1].disk_size/$diskSizeInGB
        $diskName = $result[$result.Length-1].disk_name
        write-Debug "Disk size in GB is $diskSize"
        write-Debug "Disk name is $diskName"
        return $true, $diskSize, $diskName

    }
    catch 
    {
        write-warning "Exception in getting disk resource"
        throw $_
        return $false
    }
}

<#-----FUNCTION TO CREATE STORAGE VOLUME IN THE FREENAS SERVER-----#>
Function createStorageVolume([string] $diskName, [string] $volumeName)
{


    try
    {

        #POST request for creation of new volume
        $object = [pscustomobject]@{

        volume_name = $volumeName
    

        layout = @(
                    [pscustomobject]@{
                        vdevtype = 'stripe'
                        disks = $diskName
                    }
        
                )
        }

        $volumeCreationURI = $uri+"/api/v1.0/storage/volume/"

        $postParams = $object | ConvertTo-Json
        write-debug "volume creation URI is $volumeCreationURI"
        write-Host "JOSN request for createStorageVolume is "$postParams
        $response = Invoke-WebRequest -Uri $volumeCreationURI -Headers $headers -Method POST -Body $postParams -ContentType "application/json"
        $status = [int]$response.StatusCode
        Write-Host "Response status code returned by createStorageVolume is $Status"
        Write-Host "Response returned by createStorageVolume is "$response.Content | ConvertTo-JSON

        if ($status -ne '201'){
                Write-Error "Error in creating the volume"
                return $false
       }
       return $true
    }
    catch 
    {
        write-warning "Exception in creation of volume"
        throw $_
        return $false 
    }

}

<#-----FUNCTION TO CREATE STORAGE EXTENT IN THE FREENAS SERVER-----#>
Function createStorageExtent([int] $diskSize, [string] $volumeName, [int] $index)
{

    try
    {
        $diskSizeString = $diskSize.ToString()+"GB"
        $extentName = "iSCSI_"+"SVM_STORAGE_EXTENT_"+$index.ToString()
        $extentPath= "/mnt/"+$volumeName+"/"+$extentName

        #POST request for creation of new extent
        $object = [pscustomobject]@{

        iscsi_target_extent_type = 'File'
        iscsi_target_extent_name = $extentName
        iscsi_target_extent_filesize = $diskSizeString
        iscsi_target_extent_path = $extentPath
        iscsi_target_extent_pblocksize='true'
    
        }

        $extentCreationURI = $uri+"/api/v1.0/services/iscsi/extent/"

        $postParams = $object | ConvertTo-Json
        write-debug "extent creation URI is $extentCreationURI"
        write-Host "JOSN request for createStorageExtent is "$postParams
        $response = Invoke-WebRequest -Uri $extentCreationURI -Headers $headers -Method POST -Body $postParams -ContentType "application/json"
        $status = [int]$response.StatusCode
        Write-Host "Response status code returned by createStorageExtent is "$Status

        if ($status -ne '201'){
                Write-Error "Error in creating the extent"
                return
        }
        Write-Host "JSON Response for createStorageExtent is "$response.Content | ConvertTo-JSON

        $result = $response.Content | ConvertFrom-Json
    
  
        $extentID = $result.id
        write-debug "Extent Identifier is $extentID"
        return $true,$extentID
    
   
   
    }
    catch 
    {
        write-Host "Exception in creation of extent"
        throw $_
        return $false
    }
}


<#-----FUNCTION TO CREATE TARGET TO EXTENT IN THE FREENAS SERVER-----#>
Function createTargetToExtent([int] $extentID) 
{
    
 
    try
    {
        #First Get the iSCSI target id
        $gettargetURI = $uri+"/api/v1.0/services/iscsi/target/"
        write-debug "gettargetURI is $gettargetURI"
    
        $response = Invoke-WebRequest -Uri $gettargetURI  -Headers $headers -Method Get

        $status = [int]$response.StatusCode
        Write-debug "Response status code returned by gettargetURI is $Status"

        if ($status -ne '200'){
            Write-Error "Error in retriving the target resource in createTargetToExtent"
            return $false
        }
        Write-Debug "Response from gettargetURI is $response.Content"
        $result = $response.Content | ConvertFrom-Json

        write-host "length of result returned by gettargetURI is "$result.Length

        $targetID = $result[$result.Length-1].id
        $targetName = $result[$result.Length-1].iscsi_target_name
        write-debug "iSCSI targetID is $targetID"
        write-debug "iSCSI targetName is $targetName"
    
        

        $targetToextentURI = $uri+"/api/v1.0/services/iscsi/targettoextent/"

        write-debug "Target to extent creation URI is $targetToextentURI"
        #POST request for creation of new target
        $object = [pscustomobject]@{

        iscsi_target = $targetID
        iscsi_extent = $extentID
        iscsi_lunid = $null
   
    
        }
        $postParams = $object | ConvertTo-Json
        
        write-Host "JOSN request for createTargetToExtent creation is "$postParams
        $response = Invoke-WebRequest -Uri $targetToextentURI -Headers $headers -Method POST -Body $postParams -ContentType "application/json"
        $status = [int]$response.StatusCode
        Write-Host "Response status code returned by createTargetToExtent is "$Status

        if ($status -ne '201'){
                Write-Error "Error in creating the target to extent mapping"
                return $false
        }
        Write-Host "JSON Response for createTargetToExtent is "$response.Content | ConvertTo-JSON

        $result = $response.Content | ConvertFrom-Json
    
  
        $targetToextentID = $result.id
        write-debug "Target to Extent Identifier is $targetToextentID"
    
        return $true,$targetToextentID
   
    }
    catch 
    {
        write-Host "Exception in creation of Target to extent"
        throw $_
        return $false
    }
}

<#-----FUNCTION TO DELETE STORAGE VOLUME IN THE FREENAS SERVER-----#>
Function deleteStorageVolume([string] $volumeName)
{
        Write-warning "Deleting the volume $volumeName"
        $volumeDeletionURI = $uri+"/api/v1.0/storage/volume/"+$volumeName+"/"


        write-debug "volume deletion URI is $volumeDeletionURI"

        $object = [pscustomobject]@{

        destroy = $true
        cascade = $true
        
        }

        
        $postParams = $object | ConvertTo-Json
        write-Host "JOSN request for deleteStorageVolume is "$postParams
        #write-Host "headers are "$headers.ToString()
                
        $response = Invoke-WebRequest -Uri $volumeDeletionURI -Headers $headers -Method DELETE -Body $postParams -ContentType "application/json"
        #$response = Invoke-WebRequest -Uri $volumeDeletionURI -Headers $headers -Method GET
        $status = [int]$response.StatusCode
        Write-Host "Response status code for deleteStorageVolume is "$Status

        if ($status -ne '204'){
                Write-Error "Error in deleting the storage volume"
                return
        }
        return
}


<#-----FUNCTION TO DELETE STORAGE EXTENT IN THE FREENAS SERVER-----#>
Function deleteStorageExtent([int] $extentID)
{
        Write-warning "Deleting the extent ID $extentID"
        $extentDeletionURI = $uri+"/api/v1.0/services/iscsi/extent/"+$extentID+"/"


        write-debug "extent deletion URI is $extentDeletionURI"

        $object = [pscustomobject]@{

        destroy = $true
        cascade = $true
        
        }

        $postParams = $object | ConvertTo-Json
        write-Host "JOSN request in deleteStorageExtent is "$postParams
        #write-Host "headers are "$headers.ToString()
                
        $response = Invoke-WebRequest -Uri $extentDeletionURI -Headers $headers -Method DELETE -ContentType "application/json"
        #$response = Invoke-WebRequest -Uri $volumeDeletionURI -Headers $headers -Method GET
        $status = [int]$response.StatusCode
        Write-Host "Response status code for deleteStorageExtent is "$Status

        if ($status -ne '204'){
                Write-Error "Error in deleting the storage extent"
                return
        }
        return
}



Function allocStorage() {
    <#-----STEPS FOR CREATION OF STORAGE VOLUME, EXTENT, TARGET TO EXTENT IN THE FREENAS SERVER-----#>

    <#-----1. GET THE DISK RESOURCE FROM THE FREENAS SERVER-----#>
    $return = getDISKResource $uri, $headers
    if( $return[0] -eq $false)
    {
        Write-Error " Unable to find new disk, not proceeding with further operations on FREENAS Server $server"

        return $false
    }

    $diskSize = $return[1]
    $diskName = $return[2]
    write-host "New disk size is "$diskSize"GB"
    write-host "New disk name is "$diskName

    <#-----2. CREATE THE STORAGE VOLUME IN THE FREENAS SERVER-----#>
    try
    {
        $storageVolumeName = "SVM_STORAGE_VOL_"+$index.ToString()
        $global_storageVolumnName = $storageVolumeName
        $return = createStorageVolume $diskName $storageVolumeName
        if( $return -eq $false)
        {
            Write-Error " Unable to create storage volume $storageVolumeName in the FREENAS Server $server"
            return $false
        }
    }
    catch
    {
        Write-Error "Exception in storage volume creation in the FREENAS Server $server"
        return $false
    }
        Write-Host "`nCreation of Storage Volume is done for FREENAS server $server, going forward with Storage Extent Creation`n" -ForegroundColor Green

    <#-----3. CREATE THE STORAGE EXTENT IN THE FREENAS SERVER-----#>
    try
    {

        $return = createStorageExtent $diskSize $storageVolumeName $index
        if( $return[0] -eq $false)
        {
            Write-Error " Unable to create storage extent in the FREENAS Server $server"
            deleteStorageVolume $storageVolumeName
            return $false
        }
        $extentID = $return[1]
        $global_extentID = $extentID
        write-host "Extent Identifier is "$extentID
    }
    catch
    {
        Write-Error "Exception in storage extent creation in the FREENAS Server $server"
        deleteStorageVolume $storageVolumeName
        return $false
    }

        Write-Host "`nCreation of Storage Extent creation is done for FREENAS server $server,going forward with Target to Extent Creation`n" -ForegroundColor Green

    <#-----4. CREATE THE TARGET TO EXTENT IN THE FREENAS SERVER-----#>
    try
    {

        $result = createTargetToExtent $extentID
        if( $result[0] -eq $false)
        {
            Write-Error " Unable to create target to storage extent in the FREENAS Server $server"
            deleteStorageExtent $extentID
            deleteStorageVolume $storageVolumeName
            return $false
        }
        $targetToextentID = $result[1]
        write-host "Target to Extent Identifier is "$targetToextentID

        Write-Host "`nCreation of Target to Extent is done for FREENAS server $server`n" -ForegroundColor Green
    }
    catch
    {
        Write-Error "Exception in target to extent creation in the FREENAS Server $server"
        deleteStorageExtent $extentID
        deleteStorageVolume $storageVolumeName
        return $false
    }
}


Function releaseStorage() {
    deleteStorageExtent $global_extentID
    deleteStorageVolume $global_storageVolumeName
}

if ( $action -eq 1 )
{
    allocStorage
}

if ( $action -eq 2)
{
    releaseStorage
}



