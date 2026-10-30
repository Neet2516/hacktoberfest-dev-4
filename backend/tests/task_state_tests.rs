use specter_backend::TaskStatus;

#[test]
fn test_valid_forward_transitions() {
    assert!(TaskStatus::Backlog.can_transition_to(&TaskStatus::Ready));
    assert!(TaskStatus::Ready.can_transition_to(&TaskStatus::InProgress));
    assert!(TaskStatus::InProgress.can_transition_to(&TaskStatus::Review));
    assert!(TaskStatus::Review.can_transition_to(&TaskStatus::Completed));
}

#[test]
fn test_valid_review_rejection_transition() {
    // Reviewer requests changes -> task transitions back to in-progress
    assert!(TaskStatus::Review.can_transition_to(&TaskStatus::InProgress));
}

#[test]
fn test_valid_blocker_transitions() {
    assert!(TaskStatus::InProgress.can_transition_to(&TaskStatus::Blocked));
    assert!(TaskStatus::Blocked.can_transition_to(&TaskStatus::InProgress));
    assert!(TaskStatus::Blocked.can_transition_to(&TaskStatus::Ready));
}

#[test]
fn test_invalid_bypass_transitions() {
    // Direct Backlog to Completed is strictly prohibited
    assert!(!TaskStatus::Backlog.can_transition_to(&TaskStatus::Completed));
    // Direct In-Progress to Completed without Review is strictly prohibited
    assert!(!TaskStatus::InProgress.can_transition_to(&TaskStatus::Completed));
    // Direct Backlog to Review is prohibited
    assert!(!TaskStatus::Backlog.can_transition_to(&TaskStatus::Review));
}

