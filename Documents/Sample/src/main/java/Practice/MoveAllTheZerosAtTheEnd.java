package Practice;

public class MoveAllTheZerosAtTheEnd {
    public static void main(String[] args) {
        int [] myArray={2,5,0,4,2,7,0,0,1,9,4};
        int n=myArray.length;
        int count=0;
        for (int i=0; i < n;i++){
            if (myArray[i]!=0){
                myArray[count++]=myArray[i];
            }
        }
        while (count<n){
            myArray[count++]=0;
        }
        for (int i:myArray){
            System.out.print(i+" ");
        }
    }
}
