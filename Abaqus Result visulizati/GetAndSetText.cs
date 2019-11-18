using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GetAndSetText : MonoBehaviour {

    public InputField angle;
    public InputField ratio;
    public InputField rotatePlane;
    public Slider tumorSlider;
    private Vector3 breastAngleHistory;
    private Vector3 humanPos;
    private Vector3 femaleCenter;
    private GameObject female;
    private GameObject breast;
    private GameObject tumor;

    public void Start()
    {
        breastAngleHistory = new Vector3(90f, 0f, -90f);
        humanPos = new Vector3(-21.935f, 0.268f, -0.894f);
        female = GameObject.Find("Female");
        femaleCenter = GameObject.Find("Female Center").transform.position;
        breast = GameObject.Find("Breast");
        tumor = GameObject.Find("Tumor");
    }

    public void Setget()
    {
        receive breastScript = breast.GetComponent<receive>();
        if (float.Parse(angle.text) == null || float.Parse(ratio.text) == null)
        {
            return;
        }

        float glandularFatRatio;
        float breastAngle = 180 + float.Parse(angle.text);
        glandularFatRatio = float.Parse(ratio.text);
        Vector3 direction;
        female.transform.rotation = Quaternion.Euler(breastAngleHistory);
        female.transform.localPosition = humanPos;
        if (float.Parse(rotatePlane.text) == 1)
        {
            direction = new Vector3(Mathf.Cos(breastAngle * Mathf.Deg2Rad), Mathf.Sin(breastAngle * Mathf.Deg2Rad), 0);
            female.transform.RotateAround(femaleCenter, Vector3.forward, 180f - breastAngle);
        }
        else
        {
            direction = new Vector3(0f, Mathf.Cos(breastAngle * Mathf.Deg2Rad), Mathf.Sin(breastAngle * Mathf.Deg2Rad));
            female.transform.RotateAround(femaleCenter, Vector3.left, 180f - breastAngle);
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

    public void ScaleTumorMesh()
    {
        Tumor tumorScript = tumor.GetComponent<Tumor>();
        tumorScript.ScaleTumorMesh(tumorSlider.value);
    }
}
