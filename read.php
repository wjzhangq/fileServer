<?php
$sock = fsockopen('unix:///data/tmp/t_video_reference_3.sort.json.sock', NULL, $errno, $errstr);
if (!$sock){
	var_dump($errstr);
	exit();
}

fwrite($sock, 'ccuv');
$str = fread($sock, 1024);
var_dump($str);

fclose($sock);
?>