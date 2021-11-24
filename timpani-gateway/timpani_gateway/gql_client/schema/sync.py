NODELIST_QUERY= """
        query{
            node_list(token: "X_TOKEN"){
                nodes{
                    uuid
                    node_name
                    group_id
                    group_name
                    server_uuid
                    ipmi_user_id
                    ipmi_user_password
                    bmc_mac_addr
                    bmc_ip
                    bmc_ip_subnet_mask
                    pxe_mac_addr
                    created_at
                }
            }
        }
    """

VOLUMELIST_QUERY= """
        query{
            volume_list(token: "X_TOKEN"){
                volume{
                    uuid
                    name
                    group_id
                    user_uuid
                    server_uuid
                    use_type
                    size
                }
            }
        }
    """
