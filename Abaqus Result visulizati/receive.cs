using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class receive : MonoBehaviour
{

    // Use this for initialization
    private Mesh mesh;
    private List<Vector3> vertices;  // breast vertices
    private Vector3[] tumorVertices; 
    private List<int> triangles;
    private int[] trianglesUnique;
    List<Vector3> disp;
    public string IP = "127.0.0.1"; //
    public int Port = 25001;
    public byte[] sendData;
    public Socket client;
    private float scale = 1f;
    private float yaw;
    private Vector3 needlePos;
    GameObject needle;
    private Vector3 breastCenter;
    public float arrowOffset = 50f; // height for arrow

    void Start()
    {
        gameObject.AddComponent<MeshFilter>();
        gameObject.AddComponent<MeshRenderer>();
        Color newColor = new Color(200f, 100f, 100f, 0.5f);
        gameObject.GetComponent<MeshRenderer>().material.color = new Color(1.0f, 1.0f, 1.0f, 0.5f); ;
        mesh = GetComponent<MeshFilter>().mesh;
        triangles = new List<int>();
        mesh.Clear();
        vertices = BuildVertexMesh("Breast/Skin_Layer.node");
        BuildFaceMesh("Breast/Skin_Layer.face");
        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();
        trianglesUnique = triangles.Distinct().ToArray();
        Array.Sort(trianglesUnique);
        Debug.Log(trianglesUnique.Length);
        Color[] colors = new Color[mesh.vertices.Length];
        for (int i = 0; i < mesh.vertices.Length; i++)
        {
            colors[i].r = UnityEngine.Random.Range(0f, 1.0f); //((float)i / mesh.vertices.Length);
            //   colors[i].b = Random.Range(0f, 1.0f);
            //   colors[i].g = Random.Range(0f, 0.1f);
            //   colors[i] = new Color(0.3f, 0.4f, 0.6f, 0.3f);
        }
        mesh.colors = colors;
        mesh.RecalculateNormals();
        needle = GameObject.Find("needle");
        yaw = 0f;

        breastCenter = CalculateCenter(vertices);
        GameObject tumor = GameObject.Find("tumor");
        Mesh tumorMesh = ReturnMesh(tumor);
        tumorVertices = CopyListVector3(tumorMesh.vertices);
        //  transform.Translate(-breastCenter);
    }

    // Update is called once per frame
    void Update()
    {
        // if(Input.GetKey("up"))
        {
            yaw += 2;
            //   transform.RotateAround(breastCenter, Vector3.forward, 2); // rotate around its own center

        }
        Vector3 direction = new Vector3(Mathf.Cos(yaw * Mathf.Deg2Rad), Mathf.Sin(yaw * Mathf.Deg2Rad), 0);
        Vector3 displacement = new Vector3(-7f, -6f, -2f);
        needlePos = vertices[1650];
        // needle.transform.localPosition = needlePos;
        double timeBefore = Time.realtimeSinceStartup;
        //	Changing(displacement, needlePos);
        Prediction(direction);
        double timeAfter = Time.realtimeSinceStartup;
        mesh.RecalculateNormals();
        //   GameObject.Find("ArrayStart").transform.position = breastCenter + Vector3.down * arrowOffset;
        //   GameObject.Find("ArrayEnd").transform.position = breastCenter + Vector3.down * arrowOffset + direction * 2;
    }

    // copy a list of vector3
    public static Vector3[] CopyListVector3(Vector3[] source)
    {
        Vector3[] destination = new Vector3[source.Length];
        for(int i = 0; i < source.Length; i++)
        {
            destination[i] = new Vector3(source[i].x, source[i].y, source[i].z);
        }
        return destination;
    }

    private Vector3 CalculateCenter(List<Vector3> verts)
    {
        Vector3 center = Vector3.zero;
        for (int i = 0; i < verts.Count; i++)
        {
            center += verts[i];
        }
        return center / verts.Count;
    }


    private List<Vector3> BuildVertexMesh(string nodeFile)
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

    private void BuildFaceMesh(string surfaceFile)
    {
        StreamReader reader = Reader(surfaceFile);
        string text = " ";
        text = reader.ReadLine();

        while (text != null)
        {
            string[] arr;
            arr = text.Split(' ');

            triangles.Add(int.Parse(arr[0]));
            triangles.Add(int.Parse(arr[2]));
            triangles.Add(int.Parse(arr[1]));
            text = reader.ReadLine();
        }
        reader.Close();
    }

    private StreamReader Reader(string surfaceFile)
    {
        FileInfo theSourceFile = null;
        StreamReader reader = null;
        theSourceFile = new FileInfo(surfaceFile);
        reader = theSourceFile.OpenText();
        return reader;
    }

    private List<Vector3> MoveVertices(List<Vector3> verts, List<Vector3> disp)
    {
        List<Vector3> verticesAfterDisp = new List<Vector3>();
        for (int i = 0; i < verts.Count; i++)
        {
            verticesAfterDisp.Add(verts[i] + disp[i]);
        }
        return verticesAfterDisp;
    }

    private void PrintMaxDisp(List<Vector3> verts, List<Vector3> disp)
    {
        double max = 0;
        int index = 0;
        for (int i = 0; i < disp.Count; i++)
        {
            Vector3 temp = disp[i];
            if (temp.magnitude > max)
            {
                max = temp.magnitude;
                index = i;
            }
        }

        Debug.Log(verts[index]);
    }


    private List<Vector3> MoveVerticesThreshold(List<Vector3> vertices, List<Vector3> disp, List<int> indices)
    {
        List<Vector3> verticesAfterDisp = new List<Vector3>(vertices);
        for (int i = 0; i < indices.Count; i++)
        {
            int vertex_index = trianglesUnique[indices[i]];
            verticesAfterDisp[vertex_index] = (vertices[vertex_index] + disp[i]);
        }
        return verticesAfterDisp;
    }

    // split the information recieved from python about tumor
    // return tumor center and postion
    private Vector3[] TumorStuff(string tumorInfor)
    {
        string[] tumorInfoSplit = tumorInfor.Split(' ');
        Debug.Log(tumorInfoSplit);
        string[] tumorDispStr = (tumorInfoSplit[0]).Split(',');
        string[] tumorCenterStr = tumorInfoSplit[1].Split(',');
        Vector3 tumorDisp = new Vector3(float.Parse(tumorDispStr[0]), float.Parse(tumorDispStr[1]), float.Parse(tumorDispStr[2]));
        Vector3 tumorCenter = new Vector3(float.Parse(tumorCenterStr[0]), float.Parse(tumorCenterStr[1]), float.Parse(tumorCenterStr[2]));
        return new Vector3[2] { tumorCenter, tumorDisp };
    }

    // move directly the object by adding value to each mesh point 
    private void MoveObjectMesh(GameObject obj, Vector3 vec)
    {
        Mesh objMesh = ReturnMesh(obj);
        List<Vector3> temp_vertices = new List<Vector3>();
        for (int i = 0; i < objMesh.vertexCount; i++)
        {
            temp_vertices.Add(objMesh.vertices[i] + vec);
        }
        objMesh.vertices = temp_vertices.ToArray();
    }

    // Given an object, return its mesh
    private Mesh ReturnMesh(GameObject obj)
    {
        MeshFilter filter = (MeshFilter)obj.GetComponent("MeshFilter");
        Mesh objMesh = filter.mesh;
        return objMesh;
    }

    public void Prediction(Vector3 direction)
    {
        double timeBeforeTotal = Time.realtimeSinceStartup;
        client = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        client.Connect(IP, Port);
        sendData = System.Text.Encoding.ASCII.GetBytes(direction[0].ToString("G4") + "," + direction[1].ToString("G4") + "," + direction[2].ToString("G4"));

        client.Send(sendData);
        byte[] b = new byte[100];

        int k = client.Receive(b);

        //   Debug.Log("Time for receiving data: " + (timeAfter - timeBefore).ToString());
        double timeAfterTotal = Time.realtimeSinceStartup;
        Debug.Log("Time for sending data1: " + (timeAfterTotal - timeBeforeTotal).ToString());

        string tumorInfor = System.Text.Encoding.ASCII.GetString(b, 0, k);
        Vector3[] tumor_center_disp = TumorStuff(tumorInfor);
        Vector3 tumorCeter = tumor_center_disp[0];
        Vector3 tumorDisp = tumor_center_disp[1];
        GameObject tumor = GameObject.Find("tumor");
        Mesh tumorMesh = ReturnMesh(tumor);
        tumorMesh.vertices = tumorVertices;
        MoveObjectMesh(tumor, tumorDisp + tumorCeter);     

        string szReceived = " ";
        Vector3 vertex;


        StreamReader reader = Reader("F:/Research/FEA simulation for NN/train_patient_specific/disp_prediction.txt");
        szReceived = reader.ReadLine();

        reader.Close();
        Debug.Log("Time for sending data2: " + (Time.realtimeSinceStartup - timeBeforeTotal).ToString());

        List<int> indices = new List<int>();
        if (client.Connected)
        {
            disp = new List<Vector3>();
            string[] words = szReceived.Split(',');

            for (int i = 0; i < words.Length - 4; i += 4)
            {
                int index = int.Parse(words[i]);
                float x = float.Parse(words[i + 1]) * scale;
                float y = float.Parse(words[i + 2]) * scale;
                float z = float.Parse(words[i + 3]) * scale;
                disp.Add(new Vector3(x, y, z));
                indices.Add(index);
            }
            double timeAfter = Time.realtimeSinceStartup;

            List<Vector3> verticesAfterDisp = MoveVerticesThreshold(vertices, disp, indices);

            double timeBefore = Time.realtimeSinceStartup;
            mesh.vertices = verticesAfterDisp.ToArray();
            Debug.Log("Time for reading data: " + (timeAfter - timeBefore).ToString());
            //   Debug.Log("Getting data from Python " + words.Length);
            //   Debug.Log("Start: " + words[0]);
            //   Debug.Log("End: " + words[words.Length - 5]);
        }
        else
        {
            Debug.Log(" Not Connected");

        }
        Debug.Log("Time for sending data3: " + (Time.realtimeSinceStartup - timeBeforeTotal).ToString());
        client.Close();
    }

}