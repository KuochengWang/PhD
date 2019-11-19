using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GetAndSetText : MonoBehaviour {

  //  public InputField angle;
    public InputField ratio;
    public Slider tumorSlider;
    public Slider angleSlider;
    public Dropdown rotatePlane;
    private Vector3 breastAngleHistory;
    private Vector3 humanPos;
    private Vector3 femaleCenter;
    private GameObject female;
    private GameObject breast;
    private GameObject tumor;
    private GameObject bed;
    private GameObject lowerCamera;
    private int rotatePlaneValue;
    private float angle;

    public void Start()
    {
        breastAngleHistory = new Vector3(90f, 0f, -90f);
        humanPos = new Vector3(-0f, 0f, -0f);
        female = GameObject.Find("Female");
        femaleCenter = GameObject.Find("Female Center").transform.position;
        breast = GameObject.Find("Breast");
        tumor = GameObject.Find("Tumor");
        bed = GameObject.Find("Hospital Bed");
        lowerCamera = GameObject.Find("Lower Camera");
    }

    public void GetRotatePlane(int index)
    {
        rotatePlaneValue = index;
    }

    public void Setget()
    {
        receive breastScript = breast.GetComponent<receive>();
        if (angle == null || float.Parse(ratio.text) == null)
        {
            return;
        }

        float glandularFatRatio;
        float breastAngle = 180 + angle;
        glandularFatRatio = float.Parse(ratio.text);
        Vector3 direction;
        female.transform.rotation = Quaternion.Euler(breastAngleHistory);
        female.transform.localPosition = humanPos;
        if (rotatePlaneValue == 0)
        {
            direction = new Vector3(Mathf.Cos(breastAngle * Mathf.Deg2Rad), Mathf.Sin(breastAngle * Mathf.Deg2Rad), 0);
            female.transform.RotateAround(femaleCenter, Vector3.forward, 180f - breastAngle);
            bed.transform.position = new Vector3(125.13f, -0.2f, -247.7f);
            bed.transform.eulerAngles = new Vector3(5.8f, -0.67f, -79.19801f);
            lowerCamera.transform.position = new Vector3(149.9f, -55.7f, -239.5f);
            lowerCamera.transform.eulerAngles = new Vector3(-72.3f, 268.9f, -0.2f);
        }
        else
        {
            direction = new Vector3(0f, Mathf.Cos((breastAngle + 180) * Mathf.Deg2Rad), Mathf.Sin((breastAngle + 180) * Mathf.Deg2Rad));
            female.transform.RotateAround(femaleCenter, Vector3.right, 180f - breastAngle);
            bed.transform.position = new Vector3(133.8f, 17.6f, -211.1f);
            bed.transform.eulerAngles = new Vector3(-7.9f, -89.3f, -186.3f);
            lowerCamera.transform.position = new Vector3(137.9f, -51.7f, -212f);
            lowerCamera.transform.eulerAngles = new Vector3(-85.663f, 271.435f, -3.316f);
        }        
        breastScript.Prediction(direction, glandularFatRatio);
        Vector3 offset = new Vector3(140.5f, -7.9f, 115.9f);
        
      //  GameObject.Find("DirStart").transform.position = offset;
      //  GameObject.Find("DirEnd").transform.position = offset + direction * 5;
      //  MoveArrow(offset, offset + direction * 5f, 8);
    }

    private void MoveArrow(Vector3 start, Vector3 end, int numOfArrow)
    {
        Vector3 arrowSpace = (end - start) / (numOfArrow + 1);
        for(int i = 1; i <= numOfArrow; i++)
        {
            GameObject.Find("arrow" + i.ToString()).transform.position = start + i * arrowSpace;
        }
    }

    private void CreateArrow(Vector3 start, Vector3 end)
    {
        int interval = 10;
        int arrowNumber = interval - 2;
        GameObject[] arrow = new GameObject[arrowNumber];
        Vector3 arrowSpace = (end - start) / interval;
        for (int i = 1; i < arrowNumber - 1; i++)
        {
            arrow[i] = GameObject.CreatePrimitive(PrimitiveType.Cube);
            arrow[i].transform.position = start + i * arrowSpace;
        }            
       
    }

    // get value from tumor input from user
    public void ScaleTumorMesh()
    {
        Tumor tumorScript = tumor.GetComponent<Tumor>();
        tumorScript.ScaleTumorMesh(tumorSlider.value);
    }

    public void GetAngle()
    {
        angle = angleSlider.value;
    }
}
