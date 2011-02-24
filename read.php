<?php
if (!isset($argv[1])){
	die("Usage:read.php filename\n");
}

$path = $argv[1];
if (!file_exists($path)){
	die("file is not exist!\n");
}

$path = realpath($path);

$uri = 'unix://' . $path;

$sock = fsockopen($uri, NULL, $errno, $errstr);
if (!$sock){
	var_dump($errstr);
	exit();
}


//fwrite($sock, 'ccuv');
//sleep(20);
while (true){
	$str = fread($sock, 1024);
	if ($str){
		echo $str;
	}else{
		break;
	}
}
?>