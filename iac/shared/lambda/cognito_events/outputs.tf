output "function_arn" {
  value = aws_lambda_function.event_handler.arn
}

output "iam_role_arn" {
  value = aws_iam_role.lambda.arn
}
