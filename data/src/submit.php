<html>
 <head>
  <title>PHP Test</title>
 </head>
 <body>
SUBMIT
 <?php
 # File paths
 $filepath_code = '/tmp/haskell_test.hs';
 $filepath_program_input = '/tmp/haskell_test.in';
 $filepath_program_output = '/tmp/haskell_test.out';

 # Parse url
 $url = $_SERVER['REQUEST_URI'];
 $url_components = parse_url($url); 
 parse_str($url_components['query'], $params); 

 # Save code from request to a file
 
 $file_code = fopen($filepath_code, 'w') or die('"Unable to open file!');
 fwrite($file_code, $params['input-code']);
 fclose($file_code);

 # Compile and run

 $run_command = escapeshellcmd('/etc/proskell/haskell/compile_and_run.py');
 $run_params  = '--input=' . $filepath_program_input;
 $run_params .= '--output='. $filepath_program_output;
 $run_params .= '--code=' . $filepath_code;

 $run_command .= ' '.$run_params; 
 exec($run_command, $output, $status);
 
 # Print results

 print_r($run_command);
 print_r($output);
 print_r($status);
 
 ?> 
 </body>
</html>