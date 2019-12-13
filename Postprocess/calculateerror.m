clc;
clear all;
abaqus_disp_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\12.txt';
predicted_disp_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\disp_prediction12.txt';
index_file = 'F:\Research\FEA simulation for NN\train_patient_specific\disp_prediction.txt';
triangle_file = 'F:\Research\Breast with weight\Weight in Unity V2\Breast\Skin_Layer_reference.face';
indices = dlmread(index_file);
indices = indices(1:4:end);
indices = indices + 1;
abaqus_disp = dlmread(abaqus_disp_file);
triangles = dlmread(triangle_file) + 1;
triangles = triangles';
triangles = unique(triangles(:));
abaqus_disp = abaqus_disp(triangles(indices), :);


predicted_disp = dlmread(predicted_disp_file);
error = sqrt(sum((abaqus_disp - predicted_disp).^2, 2));
sum(error)/25374
histogram(error)
save('error12.txt', 'error', '-ascii');

%% calculate error for each bin 
abaqus_disp_mag = sqrt(sum((abaqus_disp).^2, 2));
edges = [0 2.8 5.6 8.4 11.2 14];
[~,disp_bin] = histc(abaqus_disp_mag,edges);
errorrange_bin = [1 2 3 4 5];
dispvalue_bin = {};
errorvalue_bin = {};
error_avg = [];
error_std = [];
disp_bin_length = length(disp_bin);

for i = 1:length(errorrange_bin)
    dispvalue_bin(i,:) = {find(disp_bin == errorrange_bin(i))};
end

for i = 1:length(errorrange_bin)
    error_indices = dispvalue_bin{i};
    errorvalue_bin(i,:) = {error(error_indices)};
end

for i = 1:length(errorrange_bin)
    mean(errorvalue_bin{i});
    error_avg = [error_avg mean(errorvalue_bin{i})];
    error_std = [error_std (std(errorvalue_bin{i}))];
end

%% read orginal distance and save only the surface points
abaqus_dist_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\12_dist.txt'
abaqus_dist = dlmread(abaqus_dist_file);
abaqus_dist = abaqus_dist(triangles(indices), :);
save(abaqus_dist_file, 'abaqus_dist', '-ascii');