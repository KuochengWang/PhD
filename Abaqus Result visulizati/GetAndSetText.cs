using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GetAndSetText : MonoBehaviour {

    public InputField angle;

    public void setget()
    {
        GameObject breast = GameObject.Find("Breast");
        receive breastScript = breast.GetComponent<receive>();        
        if(float.Parse(angle.text) == null)
        {
            return;
        }
        float breast_angle;
        breast_angle = float.Parse(angle.text);
        Vector2 direction = new Vector3(Mathf.Cos(breast_angle * Mathf.Deg2Rad), Mathf.Sin(breast_angle * Mathf.Deg2Rad), 0);
        breastScript.Prediction(direction);
    }
}
