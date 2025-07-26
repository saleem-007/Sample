package Practice;

public class MaximumProductOfTriplet {
    public static void main(String[] args) {
        int [] arr={2,3,8,3,9,4,2};
        System.out.println(triplet(arr,arr.length));;
    }

        public static int triplet(int [] arr, int size){
            int firstLargest= Integer.MIN_VALUE;
            int secondLargest= Integer.MIN_VALUE;
            int thirdLargest= Integer.MIN_VALUE;
            for(int i = 0;i<size;i++){
                if (arr[i]>firstLargest){
                    thirdLargest=secondLargest;
                    secondLargest=firstLargest;
                    firstLargest=arr[i];
                } else if (arr[i]>secondLargest&&arr[i]!=firstLargest) {
                    secondLargest=arr[i];
                } else if (arr[i]>thirdLargest&&arr[i]!=firstLargest&arr[i]!=secondLargest) {
                    thirdLargest=arr[i];
                }
            }
            return firstLargest*secondLargest*thirdLargest;
        }
}
