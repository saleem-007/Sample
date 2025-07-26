package hackerEarth;

public class FindPalindrome {
    public static void main(String[] args) {
        String str="mom";
        String reverse="";
        for (int i=str.length()-1;i>=0;i--){
            reverse+=str.charAt(i);
        }
        if (str.equals(reverse)){
            System.out.println("Given word is Palindrome");
        }else {
            System.out.println("Given word is not a Palindrome");
        }
    }
}
