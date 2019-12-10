clc;
clear all;
abaqus_disp_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\88.txt';
predicted_disp_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\disp_prediction88.txt';
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
error = sqrt(sum((abaqus_disp - predicted_disp).^2,2));
sum(error)/25374
histogram(error)
save('error88.txt', 'error', '-ascii');


%% read orginal distance and save only the surface points
abaqus_dist_file = 'F:\Research\FEA simulation for NN\stl\Abaqus_outputs\weight\test\88_dist.txt'
abaqus_dist = dlmread(abaqus_dist_file);
abaqus_dist = abaqus_dist(triangles(indices), :);
save(abaqus_dist_file, 'abaqus_dist', '-ascii');