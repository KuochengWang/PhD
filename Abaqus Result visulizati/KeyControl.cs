using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class KeyControl : MonoBehaviour {

    private GameObject breast;
    public int cameraWidth = 400;
    public int cameraHeight = 300;
    public float cameraStartX = 200;
    public float cameraStartY = 0;

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
        if (Input.GetKey(KeyCode.P))
        {
            StartCoroutine(Capturescreen());
        }
	}

    private IEnumerator Capturescreen()
    {
        yield return new WaitForEndOfFrame();
        Texture2D tex = new Texture2D(cameraWidth, cameraHeight, TextureFormat.RGB24, false);

        tex.ReadPixels(new Rect(cameraStartX, cameraStartY, cameraWidth, cameraHeight), 0, 0);
        tex.Apply();

        // Encode texture into PNG
        var bytes = tex.EncodeToPNG();
        Destroy(tex);
        File.WriteAllBytes(Application.dataPath + "/../SavedScreen.png", bytes);
    }
}
