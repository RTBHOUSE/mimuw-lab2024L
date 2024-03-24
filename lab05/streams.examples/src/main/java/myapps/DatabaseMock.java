package myapps;

import java.util.List;

public class DatabaseMock {
    public void updateUserProfile(String userId, long count, long sum) {
        System.out.println("Updated profile " + userId + ", current count = " + count + ", current sum = " + sum);
    }

    public void batchUpdate(List<UserProfile> profiles) {
        for (UserProfile userProfile : profiles) {
            System.out.println("Fast update of " + userProfile.userId + " count = "
                    + userProfile.count + " sum = " + userProfile.sum);
        }
        System.out.println("updated " + profiles.size() + " profiles");
    }

    public static class UserProfile {
        private final String userId;
        private final long count;
        private final long sum;

        public UserProfile(String userId, long count, long sum) {
            this.userId = userId;
            this.count = count;
            this.sum = sum;
        }
    }
}
