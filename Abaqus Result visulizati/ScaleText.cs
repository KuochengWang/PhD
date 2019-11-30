using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ScaleText : MonoBehaviour {
    ColorCode colorCode;
    TextMesh textMesh;
	// Use this for initialization
	void Start () {
        textMesh = gameObject.GetComponent<TextMesh>();
        textMesh.fontSize = 30;
        textMesh.transform.position = new Vector3(154.7f, 39.4f, 92.4f);
        textMesh.transform.eulerAngles = new Vector3(-90f, -90f, 0f);
        colorCode = new ColorCode();
	}
	
	// Update is called once per frame
	void Update () {

	}

    public void writeText(string text)
    {
        textMesh.text = text;
    }
}
