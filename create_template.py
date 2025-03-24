template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .account-card { transition: transform 0.2s; }
        .account-card:hover { transform: translateY(-5px); }
        .service-badge { font-size: 0.8rem; padding: 0.3rem 0.6rem; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-user-shield me-2"></i>Account Management</a>
        </div>
    </nav>
    <div class="container mt-4">
        <div class="row">
            {% for account in accounts %}
            <div class="col-md-4 mb-4">
                <div class="card account-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title mb-0">{{ account.service }}</h5>
                            <span class="badge bg-primary service-badge">{{ account.service }}</span>
                        </div>
                        <p class="card-text">
                            <strong>Email:</strong> {{ account.email }}<br>
                            <strong>Password:</strong> {{ account.password }}<br>
                            <strong>Verification Code:</strong> {{ account.verification_code or "N/A" }}
                        </p>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="openIssueModal({{ account.id }})">
                                <i class="fas fa-exclamation-circle me-1"></i>Report Issue
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="openReplacementModal({{ account.id }})">
                                <i class="fas fa-sync-alt me-1"></i>Request Replacement
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Modals -->
    <div class="modal fade" id="issueModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Report Issue</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="issueForm">
                        <input type="hidden" id="issueAccountId">
                        <div class="mb-3">
                            <label class="form-label">Issue Type</label>
                            <select class="form-select" id="issueType" required>
                                <option value="">Select an issue type</option>
                                <option value="Incorrect Details">Incorrect Details</option>
                                <option value="Delayed Delivery">Delayed Delivery</option>
                                <option value="No Subscription">No Subscription</option>
                                <option value="Streaming Limit">Streaming Limit</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" id="issueDescription" rows="3" required></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitIssue()">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <div class="modal fade" id="replacementModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Request Replacement</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="replacementForm">
                        <input type="hidden" id="replacementAccountId">
                        <div class="mb-3">
                            <label class="form-label">Reason for Replacement</label>
                            <textarea class="form-control" id="replacementReason" rows="3" required></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitReplacement()">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let issueModal, replacementModal;
        document.addEventListener("DOMContentLoaded", function() {
            issueModal = new bootstrap.Modal(document.getElementById("issueModal"));
            replacementModal = new bootstrap.Modal(document.getElementById("replacementModal"));
        });

        function openIssueModal(accountId) {
            document.getElementById("issueAccountId").value = accountId;
            issueModal.show();
        }

        function openReplacementModal(accountId) {
            document.getElementById("replacementAccountId").value = accountId;
            replacementModal.show();
        }

        async function submitIssue() {
            const accountId = document.getElementById("issueAccountId").value;
            const issueType = document.getElementById("issueType").value;
            const description = document.getElementById("issueDescription").value;

            try {
                const response = await fetch("/api/issues", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ account_id: accountId, issue_type: issueType, description })
                });

                if (response.ok) {
                    alert("Issue reported successfully");
                    issueModal.hide();
                    document.getElementById("issueForm").reset();
                }
            } catch (error) {
                console.error("Error submitting issue:", error);
                alert("Error submitting issue");
            }
        }

        async function submitReplacement() {
            const accountId = document.getElementById("replacementAccountId").value;
            const reason = document.getElementById("replacementReason").value;

            try {
                const response = await fetch("/api/replacements", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ account_id: accountId, reason })
                });

                if (response.ok) {
                    alert("Replacement request submitted successfully");
                    replacementModal.hide();
                    document.getElementById("replacementForm").reset();
                }
            } catch (error) {
                console.error("Error submitting replacement request:", error);
                alert("Error submitting replacement request");
            }
        }
    </script>
</body>
</html>'''

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(template) 