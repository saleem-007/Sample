package hackerEarth;

public class RepeatingStringCount {
    public static void main(String[] args) {
        String str="abcdefefc";
        System.out.println( valueOfTheRepeatingString(str,str.length(),3));;
    }
    public static int valueOfTheRepeatingString(String str,int size, int k){
        int cost=0;
        for(int i=k;i<size;i+=k){
            if (!str.substring(0,k).equals(str.substring(i,i+k))){
                cost+=k*k;
            }
        }
        return cost;
    }
}
