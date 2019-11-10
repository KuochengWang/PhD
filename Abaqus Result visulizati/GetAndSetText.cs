using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GetAndSetText : MonoBehaviour {

    public InputField angle;
    public InputField ratio;

    public void setget()
    {
        GameObject breast = GameObject.Find("Breast");
        receive breastScript = breast.GetComponent<receive>();

        if (float.Parse(angle.text) == null || float.Parse(ratio.text) == null)
        {
            return;
        }

        float breastAngle, glandularFatRatio;
        breastAngle = float.Parse(angle.text);
        glandularFatRatio = float.Parse(ratio.text);
        Vector3 direction = new Vector3(Mathf.Cos(breastAngle * Mathf.Deg2Rad), Mathf.Sin(breastAngle * Mathf.Deg2Rad), 0);
        breastScript.Prediction(direction, glandularFatRatio);
    }
}
