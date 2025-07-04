•% Define the directory containing the .txt files  
directory = 'path_to_your_directory'; % Update with your directory path  
  
% Get a list of all .txt files in the directory  
fileList = dir(fullfile(directory, '*.txt'));  
  
% Loop through each file  
for i = 1:numel(fileList)  
    filename = fullfile(directory, fileList(i).name);  
     
    % Read the content of the file    fileID = fopen(filename, 'r');  
    data = textscan(fileID, '%f %f %f %f %f');    fclose(fileID);  
     
    % Apply the rules to modify the integers    modifiedData = data;    modifiedData{1}(data{1} == 7) = 0;    modifiedData{1}(data{1} == 2) = 1;    modifiedData{1}(data{1} == 8) = 2;    modifiedData{1}(data{1} == 9) = 3;    modifiedData{1}(~ismember(data{1}, [7, 2, 8, 9])) = 4; % Any other number  
     
    % Write the modified data back to the file    fileID = fopen(filename, 'w');  
    for j = 1:numel(modifiedData{1})        fprintf(fileID, '%d %.5f %.5f %.5f %.5f\n', modifiedData{1}(j), data{2}(j), data{3}(j), data{4}(j), data{5}(j));  
    end    fclose(fileID);  
end

