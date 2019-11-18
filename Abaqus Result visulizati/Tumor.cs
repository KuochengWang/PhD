using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Tumor : MonoBehaviour {
    private Vector3[] tumorVertices;
    private float tumorScale;
    Vector3 tumorCeter;
	// Use this for initialization
	void Start () {
        string breast = "Breast";
        
        Mesh tumorMesh = receive.ReturnMesh(gameObject);
        tumorVertices = receive.CopyListVector3(tumorMesh.vertices);
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    // split the information recieved from python about tumor
    // return tumor center and postion
    private Vector3[] TumorStuff(string tumorInfor)
    {
        string[] tumorInfoSplit = tumorInfor.Split(' ');
        string[] tumorDispStr = (tumorInfoSplit[0]).Split(',');
        string[] tumorCenterStr = tumorInfoSplit[1].Split(',');
        Vector3 tumorDisp = new Vector3(float.Parse(tumorDispStr[0]), float.Parse(tumorDispStr[1]), float.Parse(tumorDispStr[2]));
        Vector3 tumorCenter = new Vector3(float.Parse(tumorCenterStr[0]), float.Parse(tumorCenterStr[1]), float.Parse(tumorCenterStr[2]));
        return new Vector3[2] { tumorCenter, tumorDisp };
    }

    private void ResetTumorVertices()
    {
        Mesh tumorMesh = receive.ReturnMesh(gameObject);
        tumorMesh.vertices = tumorVertices;
    }

    // used for slider bar
    public void ScaleTumorMesh(float scale)
    {
        ResetTumorVertices();
        tumorScale = scale;
        MoveObjectMesh(gameObject, Vector3.zero, scale);
    }

    // the overall prediction is in receive.cs, this is parsing the info
    public void PredictionLocationParse(string tumorInfor)
    {
        Vector3[] tumor_center_disp = TumorStuff(tumorInfor);
        Vector3 tumorCeter = tumor_center_disp[0];
        Vector3 tumorDisp = tumor_center_disp[1];
        Mesh tumorMesh = receive.ReturnMesh(gameObject);
        tumorMesh.vertices = tumorVertices;
        tumorMesh.bounds = new Bounds(Vector3.zero, Vector3.one * 2000); // otherwise, tumor will disappear at some angle
        MoveObjectMesh(gameObject, tumorDisp + tumorCeter, tumorScale);
    }

    // move directly the object by adding value to each mesh point 
    private void MoveObjectMesh(GameObject obj, Vector3 vec, float scale)
    {
        Mesh objMesh = receive.ReturnMesh(obj);
        List<Vector3> temp_vertices = new List<Vector3>();
        for (int i = 0; i < objMesh.vertexCount; i++)
        {
            temp_vertices.Add(objMesh.vertices[i] * scale + vec);
        }
        objMesh.vertices = temp_vertices.ToArray();
    }
}
