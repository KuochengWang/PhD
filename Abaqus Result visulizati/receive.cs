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
    private List<Vector3> vertices;
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
        mesh = GetComponent<MeshFilter>().mesh;
        triangles = new List<int>();
        mesh.Clear();
        vertices = buildVertexMesh("Breast/Skin_Layer.node");
        buildFaceMesh("Breast/Skin_Layer.face");
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
        breastCenter = calculateCenter(vertices);
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
        GameObject.Find("ArrayStart").transform.position = breastCenter + Vector3.down * arrowOffset;
        GameObject.Find("ArrayEnd").transform.position = breastCenter + Vector3.down * arrowOffset + direction * 2;
    }

    void OnGUI()
    {
        GUI.Label(new Rect(0, 0, 100, 100), (1f / Time.smoothDeltaTime).ToString());
    }

    private Vector3 calculateCenter(List<Vector3> verts)
    {
        Vector3 center = Vector3.zero;
        for(int i = 0; i < verts.Count; i++)
        {
            center += verts[i];
        }
        return center / verts.Count;
    }

    // To show the lines in the game window whne it is running
    void OnPostRender()
    {
         Vector3 direction = new Vector3(Mathf.Cos(yaw * Mathf.Deg2Rad), Mathf.Sin(yaw * Mathf.Deg2Rad), 0);
         drawLine(breastCenter, direction * 100);
    }

    // To show the lines in the editor
    void OnDrawGizmos()
    {
        Vector3 direction = new Vector3(Mathf.Cos(yaw * Mathf.Deg2Rad), Mathf.Sin(yaw * Mathf.Deg2Rad), 0);
        drawLine(breastCenter, direction * 100);
    }

    private void drawLine(Vector3 lineStart, Vector3 lineEnd)
    {
        GL.Begin(GL.LINES);
        GL.Color(new Color(0, 100, 100));
        GL.Vertex3(lineStart.x, lineStart.y, lineStart.z);
        GL.Vertex3(lineEnd.x, lineEnd.y, lineEnd.z);
        GL.End();
    }

    private List<Vector3> buildVertexMesh(string nodeFile)
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

    public void Prediction(Vector3 direction)
    {
        client = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        client.Connect(IP, Port);
        sendData = System.Text.Encoding.ASCII.GetBytes(direction[0].ToString("G4") + "," + direction[1].ToString("G4") + "," + direction[2].ToString("G4"));
        double timeBeforeTotal = Time.realtimeSinceStartup;
        client.Send(sendData);
        byte[] b = new byte[(int)Mathf.Pow(2, 20f)];
        double timeBefore = Time.realtimeSinceStartup;
        int k = client.Receive(b);
        double timeAfter = Time.realtimeSinceStartup;
        //   Debug.Log("Time for receiving data: " + (timeAfter - timeBefore).ToString());
        double timeAfterTotal = Time.realtimeSinceStartup;
        //   Debug.Log("Time for sending data: " + (timeAfterTotal - timeBeforeTotal).ToString());
        string szReceived = System.Text.Encoding.ASCII.GetString(b, 0, k);
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
            List<Vector3> verticesAfterDisp = MoveVerticesThreshold(vertices, disp, indices);
            mesh.vertices = verticesAfterDisp.ToArray();
            Debug.Log("Getting data from Python " + words.Length);
         //   Debug.Log("Start: " + words[0]);
         //   Debug.Log("End: " + words[words.Length - 5]);
        }
        else
        {
            Debug.Log(" Not Connected");

        }
        client.Close();
    }

    public void ChangingThreshold(Vector3 needleTip, Vector3 pointPos)
    {
        client = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        client.Connect(IP, Port);
        sendData = System.Text.Encoding.ASCII.GetBytes(needleTip[0].ToString("G4") + "," + needleTip[1].ToString("G4") + "," + needleTip[2].ToString("G4") + "," + pointPos[0].ToString("G4") + "," + pointPos[1].ToString("G4") + "," + pointPos[2].ToString("G4"));
        double timeBeforeTotal = Time.realtimeSinceStartup;
        client.Send(sendData);
        byte[] b = new byte[(int)Mathf.Pow(2, 19f)];
        double timeBefore = Time.realtimeSinceStartup;
        int k = client.Receive(b);
        double timeAfter = Time.realtimeSinceStartup;
        //   Debug.Log("Time for receiving data: " + (timeAfter - timeBefore).ToString());
        double timeAfterTotal = Time.realtimeSinceStartup;
        //   Debug.Log("Time for sending data: " + (timeAfterTotal - timeBeforeTotal).ToString());
        string szReceived = System.Text.Encoding.ASCII.GetString(b, 0, k);
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
            List<Vector3> verticesAfterDisp = MoveVerticesThreshold(vertices, disp, indices);
            mesh.vertices = verticesAfterDisp.ToArray();
            Debug.Log("Getting data from Python " + words.Length);
        //    Debug.Log("Start: " + words[0]);
          //  Debug.Log("End: " + words[words.Length - 5]);
        }
        else
        {
            Debug.Log(" Not Connected");

        }
        client.Close();
    }
}
