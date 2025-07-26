package Practice.Strings;

public class StringRotationCheck {
    public static void main(String[] args) {
        String str1="abcd";
        String str2="cdab";
        if (str1.length()==str2.length()&&(str1+str2).contains(str2)){
            System.out.println("Given string2 is a rotation of string1");
        }else {
            System.out.println("Given string2 is not a rotation of string1");
        }
    }
}
