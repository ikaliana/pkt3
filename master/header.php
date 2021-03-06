<?php 
include './config.php';
include './user_access.php';
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
    <title><?php echo $page_title; ?></title>
    <!-- Favicon-->
    <link rel="icon" href="favicon.png" type="image/x-icon">

    <!-- Google Fonts -->
    <link href="fonts/fonts.css?family=Roboto:400,700&subset=latin,cyrillic-ext" rel="stylesheet" type="text/css">
    <link href="fonts/icon.css?family=Material+Icons" rel="stylesheet" type="text/css">
	
	<!-- Jquery Core Js -->
    <script src="plugins/jquery/jquery.min.js"></script>
	
	<!-- Malsup Jquery Form -->
	<script src="plugins/malsup/jquery.form.js"></script> 
	
    <!-- Bootstrap Core Css -->
    <link href="plugins/bootstrap/css/bootstrap.css" rel="stylesheet">
	
	<!-- Bootstrap select -->
	<link href="plugins/bootstrap-select/css/bootstrap-select.css" rel="stylesheet"/>
	
	<!-- Sweetalert Css -->
    <link href="plugins/sweetalert/sweetalert.css" rel="stylesheet" />
	
	<!-- Leqafletjs -->
    <link href="plugins/leaflet/leaflet.css" rel="stylesheet" />
	<script src="plugins/leaflet/leaflet.js"></script>
    <script src="plugins/proj4leaflet/proj4.js"></script>
    <script src="plugins/proj4leaflet/proj4leaflet.js"></script>
	
	<!-- Bootstrap Tagsinput Css -->
    <link href="plugins/bootstrap-tagsinput/bootstrap-tagsinput.css" rel="stylesheet">

    <!-- Waves Effect Css -->
    <link href="plugins/node-waves/waves.css" rel="stylesheet" />
	
	<!-- JQuery DataTable Css -->
    <link href="plugins/jquery-datatable/skin/bootstrap/css/dataTables.bootstrap.css" rel="stylesheet">
    <script src="plugins/jquery-datatable/jquery.dataTables.js"></script>
    <script src="plugins/jquery-datatable/skin/bootstrap/js/dataTables.bootstrap.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/dataTables.buttons.min.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/buttons.flash.min.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/jszip.min.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/pdfmake.min.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/vfs_fonts.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/buttons.html5.min.js"></script>
    <script src="plugins/jquery-datatable/extensions/export/buttons.print.min.js"></script>

    <!-- Animation Css -->
    <link href="plugins/animate-css/animate.css" rel="stylesheet" />

    <!-- Morris Chart Css-->
    <!-- <link href="plugins/morrisjs/morris.css" rel="stylesheet" /> -->

    <!-- Custom Css -->
    <link href="css/style.css" rel="stylesheet">

    <!-- AdminBSB Themes. You can choose a theme from css/themes instead of get all themes -->
    <link href="css/themes/all-themes.css" rel="stylesheet" />
	
	<!--File input plugin-->
	<link href="plugins/input-file/css/fileinput.min.css" media="all" rel="stylesheet" type="text/css" />
	
	<!-- datepicker-->
	<link rel="stylesheet" href="plugins/datepicker/css/datepicker.css">
	
    <!-- Bootstrap slider -->
    <link href="plugins/bootstrap-slider/css/bootstrap-slider.css" rel="stylesheet"/>
    <script src="plugins/bootstrap-slider/js/bootstrap-slider.js"></script>
    <style type="text/css">
        .map-label { color: #000; /*font-size: small;*/ }
        #mapid3 { background-color: #bcbcbc; }
        .navbar-brand img { margin-top: -24px; display: inline-block; margin-right: 12px; }
    </style>

<?php
    $page = '';
    if (isset($_GET['p'])) {
        $page = $_GET['p'];
    }
    if ($page=="hasil_content_detail") {
?>	
    <style type="text/css">
        .dt-buttons { float: right !important; }
        #tabel_rekomendasi_blok_wrapper .col-sm-6 { margin-bottom: 5px;  }
        ul.up-menu { border-bottom-color: #fff }
        ul.up-menu li a:hover { background-color: #ddd !important; }
        .header-tab-menu { 
            position: fixed;
            top: 70px;
            left: 315px;
            z-index: 3;
            background-color: #fff;
            width: 100%;
            padding-bottom: 5px;
            border-bottom: 1px solid #ddd
        }
        .header-tab-menu ul li a { 
            border: 1px solid #ccc !important; 
            border-bottom-left-radius: 7px; 
            border-bottom-right-radius: 7px;
            background-color: #efefef;
            color: #555 !important;
        }
    </style>
<?php } ?>
</head>

<body class="theme-light-green" style="background-image: url('images/background.jpg');background-repeat: no-repeat;background-attachment: fixed;background-position: center; ">
    <!-- Page Loader -->
    <div class="page-loader-wrapper">
        <div class="loader">
            <div class="preloader">
                <div class="spinner-layer pl-red">
                    <div class="circle-clipper left">
                        <div class="circle"></div>
                    </div>
                    <div class="circle-clipper right">
                        <div class="circle"></div>
                    </div>
                </div>
            </div>
            <p>Please wait...</p>
        </div>
    </div>
    <!-- #END# Page Loader -->
    <!-- Overlay For Sidebars -->
    <div class="overlay"></div>
    <!-- #END# Overlay For Sidebars -->
    <!-- Search Bar -->
    <div class="search-bar">
        <div class="search-icon">
            <i class="material-icons">search</i>
        </div>
        <input type="text" placeholder="START TYPING...">
        <div class="close-search">
            <i class="material-icons">close</i>
        </div>
    </div>
    <!-- #END# Search Bar -->
    <!-- Top Bar -->
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <!-- <a href="javascript:void(0);" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse" aria-expanded="false"></a> -->
                <a href="javascript:void(0);" class="bars"></a>
                <a class="navbar-brand font-20 font-bold" href="index.php">
                    <img src="images/logo_precipalm.png" style="height: 70px;"/>
                    <span class="hidden-xs"><?php echo $page_title; ?></span>
                </a>
            </div>
            <!-- <div class="collapse navbar-collapse" id="navbar-collapse">
                <ul class="nav navbar-nav navbar-right">
                    <li></li>
                </ul>
            </div> -->
        </div>
    </nav>