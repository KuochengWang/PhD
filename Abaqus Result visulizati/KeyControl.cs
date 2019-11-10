using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class KeyControl : MonoBehaviour {

    GameObject breast;

	// Use this for initialization
	void Start () {
        breast = GameObject.Find("Breast");        
	}
	
	// Update is called once per frame
	void Update () {
        receive breastScript = breast.GetComponent<receive>();
        if (Input.GetKey(KeyCode.W))
        {
           breast.transform.RotateAround(breastScript.breastCenter, Vector3.forward, 2); ;
        }
        if (Input.GetKey(KeyCode.S))
        {
            breast.transform.RotateAround(breastScript.breastCenter, Vector3.back, 2); ;
        }
        if (Input.GetKey(KeyCode.A))
        {
            breast.transform.RotateAround(breastScript.breastCenter, Vector3.right, 2); ;
        }
        if (Input.GetKey(KeyCode.D))
        {
            breast.transform.RotateAround(breastScript.breastCenter, Vector3.left, 2); ;
        }
	}
}
