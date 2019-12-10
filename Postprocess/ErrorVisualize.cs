using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

public class ErrorVisualize {

    public List<float> ReadError(string errorFile)
    {
        string text = " ";
        StreamReader reader = receive.Reader(errorFile);
        text = reader.ReadLine();
        List<float> errors = new List<float>();
        while (text != null)
        {       
            float error = float.Parse(text);
            errors.Add(error);
            text = reader.ReadLine();
        }
        Debug.Log(errors[0]);
        reader.Close();
        return errors;
    }

    public void AddColor(Mesh mesh, List<float> errors, List<int> surfaceIndices, int[] surfaceValues)
    {
        float[] errorsArray = errors.ToArray();
        float maxError = Mathf.Max(errorsArray);
        float minError = Mathf.Min(errorsArray);
        Vector3[] vertices = mesh.vertices;
        Color[] colors = new Color[vertices.Length];
        float interval = (maxError - minError) / (ColorCode.colorCode.Length - 1);
        for (int i = 0; i < surfaceIndices.Count; i++)
        {
            int vertexIndex = surfaceValues[surfaceIndices[i]];            
            colors[vertexIndex] = ColorCode.CalculateColor(errors[i], minError, interval);
               
        }
        
        mesh.colors = colors;
    }
}
