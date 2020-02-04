<?php
/*
		mkdir('./uploads/citra/test4',0777);
		chmod('./uploads/citra/test4',0777);
		mkdir('./uploads/citra/test4/anaknya',0777);
		chmod('./uploads/citra/test4/anaknya',0777);		
		mkdir('./result/coba',0777);
		chmod('./result/coba',0777);
		mkdir('./result/coba/anak',0777);
		chmod('./result/coba/anak',0777);
		$content = "some text here";
		$fp = fopen("./result/coba/anak/coba.txt","wb");
		fwrite($fp,$content);
		fclose($fp);
		echo("Coba 8");
*/

	chdir('../scripts');
	$script_path = getcwd()."/testcreate.py";
	echo($script_path);
	exec("python --version",$output,$ret);
	echo("Coba create pake script<br>");
	print_r($output);

	try {

		// if(!mkdir('./uploads/citra/test',777,True)) 
		// {
		// 	echo "gagal dong";
		// }
		// else echo("Done");
	}
	catch (Throwable $t) {
		echo "Oh tidak!|".$t->getMessage()."|error";
	}
?>