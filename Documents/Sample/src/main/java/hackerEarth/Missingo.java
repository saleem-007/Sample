package hackerEarth;

public class Missingo {
    public static void main(String[] args) {
        int [] arr={1,2,4};
        System.out.println(missingValue(arr,arr.length));;
    }

    public static int missingValue(int [] arr, int size){
        int result=size*(size+1)/2;
        int sum=0;
        for(int i = 0; i<size-1;i++){
            sum=sum+arr[i];
        }
        return result-sum;
    }
}
