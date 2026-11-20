data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

resource "aws_default_security_group" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-default-closed"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-internet"
  }
}

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 1)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "${local.name_prefix}-public-${count.index + 1}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-public"
  }
}

resource "aws_route" "internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "api_link" {
  name        = "${local.name_prefix}-api-link"
  description = "API Gateway VPC link to the internal load balancer"
  vpc_id      = aws_vpc.main.id
}

resource "aws_security_group" "api_lb" {
  name        = "${local.name_prefix}-api-lb"
  description = "Internal load balancer accepting only VPC link traffic"
  vpc_id      = aws_vpc.main.id
}

resource "aws_security_group" "api_task" {
  name        = "${local.name_prefix}-api-task"
  description = "API tasks accepting only load balancer traffic"
  vpc_id      = aws_vpc.main.id
}

resource "aws_vpc_security_group_egress_rule" "api_link_to_lb" {
  security_group_id            = aws_security_group.api_link.id
  referenced_security_group_id = aws_security_group.api_lb.id
  description                  = "Forward VPC link requests to the internal ALB"

  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80
}

resource "aws_vpc_security_group_ingress_rule" "api_lb_from_link" {
  security_group_id            = aws_security_group.api_lb.id
  referenced_security_group_id = aws_security_group.api_link.id
  description                  = "Accept requests only from the API Gateway VPC link"

  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80
}

resource "aws_vpc_security_group_egress_rule" "api_lb_to_task" {
  security_group_id            = aws_security_group.api_lb.id
  referenced_security_group_id = aws_security_group.api_task.id
  description                  = "Forward application requests and health checks"

  ip_protocol = "tcp"
  from_port   = 8000
  to_port     = 8000
}

resource "aws_vpc_security_group_ingress_rule" "api_task_from_lb" {
  security_group_id            = aws_security_group.api_task.id
  referenced_security_group_id = aws_security_group.api_lb.id
  description                  = "Accept application traffic only from the internal ALB"

  ip_protocol = "tcp"
  from_port   = 8000
  to_port     = 8000
}

# Development topology: tasks use public IPs for outbound HTTPS access
# to AWS service endpoints. No inbound public application access is allowed.
# Replace this with private subnets and controlled service endpoints when
# stricter outbound restrictions are required.
# trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "api_task_https" {
  security_group_id = aws_security_group.api_task.id
  description       = "Outbound HTTPS to AWS service endpoints"
  cidr_ipv4         = "0.0.0.0/0"

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443
}
