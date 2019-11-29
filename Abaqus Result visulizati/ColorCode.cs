using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ColorCode {

    Color[] colorCode = new Color[5] { Color.blue, Color.cyan, Color.green, Color.yellow, Color.red};
    
    public void AddColor(Mesh mesh, List<Vector3> displacements, List<int> surfaceIndices, int[] surfaceValues)
    {       
        Vector3 maxVector = Vector3.zero;
        Vector3 minVector = Vector3.positiveInfinity; 
        for(int i = 0; i < displacements.Count; i++)
        {          
            maxVector = (displacements[i].magnitude > maxVector.magnitude) ? displacements[i] : maxVector;
            minVector = (displacements[i].magnitude < minVector.magnitude) ? displacements[i] : minVector;
        }
        float interval = ((maxVector.magnitude - minVector.magnitude) / (colorCode.Length - 1));
        Vector3[] vertices = mesh.vertices;
        int[] faces = mesh.triangles;
        Debug.Log(vertices.Length + " " + displacements.Count);
        Color[] colors = new Color[vertices.Length];
        for (int i = 0; i < surfaceIndices.Count; i++)
        {
            int vertexIndex = surfaceValues[surfaceIndices[i]];
            int colorIndex = (int)(((displacements[i]).magnitude - minVector.magnitude) / interval);
            if (colorIndex == colorCode.Length - 1)
            {
                colors[vertexIndex] = colorCode[colorIndex];
                continue;
            }                
            float hue1, saturation1, value1;
            Color.RGBToHSV(colorCode[colorIndex], out hue1, out saturation1, out value1);
            float hue2, saturation2, value2;
            Color.RGBToHSV(colorCode[colorIndex + 1], out hue2, out saturation2, out value2);
            Color interpolatedColor = Color.Lerp(new Color(hue1, saturation1, value1), new Color(hue2, saturation2, value2), ((displacements[i]).magnitude - minVector.magnitude) / interval - colorIndex);
            colors[vertexIndex] = Color.HSVToRGB(interpolatedColor[0], interpolatedColor[1], interpolatedColor[2]);
        } 
        mesh.colors = colors;
        mesh.RecalculateNormals();
    }
}
