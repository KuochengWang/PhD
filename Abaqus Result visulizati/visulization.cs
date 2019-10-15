using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
public class visulization : MonoBehaviour {

	// Use this for initialization
    Mesh mesh;
    List<Vector3> vertices;
    List<int> triangles;
    GameObject hand;
    void Start()
    {
        gameObject.AddComponent<MeshFilter>();
        gameObject.AddComponent<MeshRenderer>();
        mesh = GetComponent<MeshFilter>().mesh;
        gameObject.GetComponent<Renderer>().material = Resources.Load("breast", typeof(Material)) as Material;  
        triangles = new List<int>();
        mesh.Clear();
        vertices = buildVertexMesh("breast_model/breastshellnode.txt", 1f);
        buildFaceMesh("breast_model/breastshellelement.txt");
        List<Vector3> disp = BuildDisp("breast_model/train2968.txt");
        Debug.Log(disp.Count);
        Debug.Log(vertices.Count);
        List<Vector3> verticesAfterDisp = MoveVertices(vertices, disp);
        mesh.vertices = verticesAfterDisp.ToArray();
        mesh.triangles = triangles.ToArray();
        hand = GameObject.Find("hand");
        PrintMaxDisp(verticesAfterDisp, disp);
        Color[] colors = new Color[mesh.vertices.Length];
        for (int i = 0; i < mesh.vertices.Length; i++)
        {
            colors[i].r = UnityEngine.Random.Range(0.5f, 1.0f); //((float)i / mesh.vertices.Length);
            colors[i].b = 0f;
            colors[i].g = 0f;
            //   colors[i] = new Color(0.3f, 0.4f, 0.6f, 0.3f);
        }
        mesh.colors = colors;
        
    }
	
	
	// Update is called once per frame
	void Update () {
		
	}

    private List<Vector3> buildVertexMesh(string nodeFile, float scale)
    {
        string text = " ";
        Vector3 vertex;
        StreamReader reader = Reader(nodeFile);
        text = reader.ReadLine();
        List<Vector3> verts = new List<Vector3>();
        while (text != null)
        {
            string[] arr;
            arr = text.Split(' ');
            vertex = new Vector3(float.Parse(arr[0]) * scale, float.Parse(arr[1]) * scale, float.Parse(arr[2]) * scale);
            verts.Add(vertex);
            text = reader.ReadLine();//Debug.Log(vertex[0]+" "+vertex[1]+" "+vertex[2]);
        }
        reader.Close();
        return verts;
    }

    private void buildFaceMesh(string surfaceFile)
    {
        StreamReader reader = Reader(surfaceFile);
        string text = " ";
        text = reader.ReadLine();

        while (text != null)
        {
            string[] arr;
            arr = text.Split(' ');
            
            triangles.Add(int.Parse(arr[0])-1);
            triangles.Add(int.Parse(arr[1])-1);
            triangles.Add(int.Parse(arr[2])-1);
            text = reader.ReadLine();
        }

        reader.Close();
    }

    private List<Vector3> BuildDisp (string disp)
    {
        float scale = 1f;
        return buildVertexMesh(disp,scale) ; 
    }

    private StreamReader Reader (string surfaceFile)
    {
        FileInfo theSourceFile = null;
        StreamReader reader = null;   
        theSourceFile = new FileInfo(surfaceFile);
        reader = theSourceFile.OpenText();
        return reader;
    }

    private List<Vector3> MoveVertices (List<Vector3> verts, List<Vector3> disp)
    {
        List<Vector3> verticesAfterDisp = new List<Vector3>();
        for (int i = 0; i < verts.Count(); i++)
        {
            verticesAfterDisp.Add(verts[i] + disp[i]);
        }
        return verticesAfterDisp;
    }

    private void PrintMaxDisp(List<Vector3> verts, List<Vector3> disp)
    {
        double max = 0;
        int index = 0;
        double ymax = 0;
        int indexYmax = 0;
        for(int i=0; i < verts.Count; i++)
        {
            Vector3 temp = disp[i];
            if(temp.magnitude > max)
            {
                max = temp.magnitude;
                index = i;
            }
            if(disp[i].y > ymax)
            {
                ymax = disp[i].y;
                indexYmax = i;
            }
        }

        Debug.Log(index + " " + disp[index]);
        hand.transform.localPosition = verts[index];
    }
}
