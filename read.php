<?php
$sock = fsockopen('unix:///Users/zhangwenjin/tmp/filesock/a.log.sock', NULL, $errno, $errstr);
if (!$sock){
	var_dump($errstr);
	exit();
}

fwrite($sock, 'ccuv');
$str = fread($sock, 1024);
var_dump($str);

fclose($sock);
?>