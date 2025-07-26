package Practice;

public class MaximumConsecutiveOnesOrZeros {
    public static void main(String[] args) {
        int [] arr = {1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1};
        System.out.println(maxConsecutive(arr,arr.length));
    }

    public static int maxConsecutive(int [] arr, int size){
        int maxOne=0, count=1;
        for (int i = 1; i <size; i++){
            if (arr[i]==arr[i-1]){
                count++;
            }else {
                count=1;
            }
        }
        Math.max(count,maxOne);
//        if (count > maxOne) {
//            maxOne = count;
//        }
        return Math.max(count,maxOne);
    }
}
