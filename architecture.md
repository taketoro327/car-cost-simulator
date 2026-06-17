%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0f172a', 'edgeLabelBackground':'#f8fafc', 'tertiaryColor': '#f1f5f9'}}}%%
graph TD
    %% --- External Net ---
    subgraph OnPrem [社内ネットワーク / On-Premise Network]
        direction TB
        Desktop[会社支給端末 / ノートPC]
        router[VPN/DC ルーター]
        Desktop -. "会社承認VPN" .-> router
    end

    %% --- AWS Cloud ---
    subgraph AWS [AWS Cloud (Region)]
        direction TB

        %% --- Direct Connect / VPN ---
        dx[AWS Direct Connect / VPN]
        router -->|プライベート接続| dx

        %% --- VPC ---
        subgraph VPC [Amazon VPC (Isolated)]
            %% --- Internet隔離の前提 ---
            IGW[<font color='red'>Internet Gateway 設置なし</font>]
            NAT[<font color='red'>NAT Gateway 設置なし</font>]
            
            direction TB
            tgw[AWS Transit Gateway]
            dx --> tgw
            tgw -->|VPC Attachment| VPC

            %% --- Security Groups (Metaphor) ---
            sg_app[SG: アプリ用]
            sg_data[SG: データ用]
            sg_vpce[SG: エンドポイント用]

            %% --- Availability Zone A ---
            subgraph AZ_A [Availability Zone A]
                direction TB
                
                %% Subnet: App
                subgraph Subnet_App_A [Private Subnet: App]
                    AGW_Pri_A[Amazon API Gateway <br/>(Private Endpoint)]
                    Lambda_A[AWS Lambda / ECS <br/>(VPC内)]
                    AGW_Pri_A -->|Invoke| Lambda_A
                end
                Lambda_A -.-> sg_app

                %% Subnet: Data
                subgraph Subnet_Data_A [Private Subnet: Data]
                    AOS_A[Amazon OpenSearch Service <br/>(Vector DB, VPC配置)]
                end
                AOS_A -.-> sg_data

                %% Subnet: Endpoints
                subgraph Subnet_VPCE_A [Private Subnet: Endpoints]
                    VPCE_Bedrock_A[Bedrock Runtime <br/>Interface Endpoint]
                    VPCE_S3_A_Int[S3 <br/>Interface Endpoint]
                end
                VPCE_Bedrock_A -.-> sg_vpce
                VPCE_S3_A_Int -.-> sg_ vpce
            end

            %% --- Availability Zone B (HA) ---
            subgraph AZ_B [Availability Zone B (High Availability)]
                direction TB
                
                %% Subnet: App
                subgraph Subnet_App_B [Private Subnet: App]
                    AGW_Pri_B[Amazon API Gateway <br/>(Private Endpoint)]
                    Lambda_B[AWS Lambda / ECS]
                    AGW_Pri_B -->|Invoke| Lambda_B
                end
                
                %% Subnet: Data
                subgraph Subnet_Data_B [Private Subnet: Data]
                    AOS_B[Amazon OpenSearch Service]
                end
                
                %% Subnet: Endpoints
                subgraph Subnet_VPCE_B [Private Subnet: Endpoints]
                    VPCE_Bedrock_B[Bedrock Runtime]
                    VPCE_S3_B_Int[S3]
                end
            end

            %% --- Communication Flow (AZ A) ---
            Desktop -.->|443/https| router
            tgw -->|Direct to AGW VPCE| AGW_Pri_A
            Lambda_A -->|Embed/Query| AOS_A
            Lambda_A -->|S3 Private API Access| VPCE_S3_A_Int
            Lambda_A -->|Bedrock Private API Access| VPCE_Bedrock_A

        end

        %% --- AWS Global Services (VPC外、PrivateAccess) ---
        VPCE_Bedrock_A -->|AWS PrivateLink| Bedrock_Service[Amazon Bedrock <br/>Service]
        Bedrock_Service <-->|学習利用なし| Models[Claude 3, etc.]

        VPCE_S3_A_Int -->|AWS PrivateLink| S3_Service[Amazon S3 <br/>Service]
        
        %% S3 Gateway Endpoint (Classic but secure for S3 only)
        Lambda_A ==>|Gateway VPCE| S3_Gate[S3 Gateway Endpoint]
        S3_Gate --> S3_Service

    end

    %% --- Styling ---
    classDef isolated stroke-dasharray: 5 5, stroke:#ef4444, fill:#fff1f1;
    classDef secure fill:#e0f2fe,stroke:#0369a1,stroke-width:2px;
    classDef data fill:#f0fdf4,stroke:#166534,stroke-width:1px;
    classDef outside fill:#f1f5f9,stroke:#94a3b8;
    classDef flow stroke:#0284c7,stroke-width:2px;
    classDef user stroke:#10b981,stroke-width:2px;

    class IGW,NAT isolated;
    class VPC,Subnet_App_A,Subnet_App_B,Subnet_VPCE_A,Subnet_VPCE_B secure;
    class Subnet_Data_A,Subnet_Data_B data;
    class Bedrock_Service,S3_Service,OnPrem outside;
    class dx,tgw flow;
    class Desktop user;
