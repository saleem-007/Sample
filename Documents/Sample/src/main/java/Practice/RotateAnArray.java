package Practice;

public class RotateAnArray {
    public static void main(String[] args) {
        int arr[] = {1, 2, 3, 4, 5, 6, 7};
        int d = 3;
        for (int i=0;i<d;i++){
            int first=arr[0];
            for (int j=0;j<arr.length-1;j++){
                arr[j]=arr[j+1];
            }
            arr[arr.length-1]=first;
        }

        for (int j:arr){
            System.out.print(j+" ");
        }
    }
}
