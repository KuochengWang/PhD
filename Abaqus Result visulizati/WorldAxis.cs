using UnityEngine;
using System.Collections;

public class WorldAxis : MonoBehaviour
{
    public float size = 1f;

    void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawLine(Vector3.right * size + gameObject.transform.position, Vector3.zero + gameObject.transform.position);

        Gizmos.color = Color.green;
        Gizmos.DrawLine(Vector3.up * size + gameObject.transform.position, Vector3.zero + gameObject.transform.position);

        Gizmos.color = Color.blue;
        Gizmos.DrawLine(Vector3.forward * size + gameObject.transform.position, Vector3.zero + gameObject.transform.position);
        Gizmos.color = Color.white;
    }
}