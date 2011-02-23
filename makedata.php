<?php
for ($i=0; $i<100; $i++){
	$str = $i < 10 ? '0' . $i : $i;
	$str = str_repeat($str, 5);
	echo $str;
	echo "\n";
}

?>