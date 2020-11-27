import subprocess
from datetime import datetime
# from ..constants import Constants

class ShellParser:

    @staticmethod
    def geom_disk_parser(node_ip):
        """
            Example Input : Name  Status  Components
                            da0     N/A  N/A
                            da1     N/A  N/A
                            da2     N/A  N/A
                            da3     N/A  N/A
                            cd0     N/A  N/A
                            
                            'Name\tStatus\tComponents\n\tda0\tN/A\tN/A\n\tda1\tN/A\tN/A\n\tda2\tN/A\tN/A\n\tda3\tN/A\tN/A\n\tcd0\tN/A\tN/A\n'

            Output : ['da0', 'da1', 'da2', 'da3']

        """
        tmp_disk_list = subprocess.run('ssh root@{} geom disk status'.format(node_ip), shell=True, encoding='utf8', capture_output=True)
        _ = tmp_disk_list.stderr
        split_disk_list = tmp_disk_list.stdout.split()
        result = [split_disk_list[i] for i in range(3, len(split_disk_list), 3) if 'cd' not in split_disk_list[i]]
        
        return result

    @staticmethod
    def _get_pool_idx(lst):
        pool_idx_list = []
        for idx, data in enumerate(lst):
            pool_name = data.split('\t')[0]
            if pool_name:
                pool_idx_list.append(idx)
        pool_idx_list.append(idx + 1)

        return pool_idx_list

    @staticmethod
    def _split_by_pool(shell_result, pool_idx_list):
        pool_list = []
        for idx, data in enumerate(pool_idx_list):
            temp_idx = idx + 1
            try:
                pool_list.append(shell_result[data:pool_idx_list[temp_idx]])
            except:
                break

        return pool_list

    @staticmethod
    def zpool_list_parser(node_ip):
        """
        Example Input: 
        data	19.5G	640K	19.5G	-	-	0%	0%	1.00x	ONLINE	-
                da3	19.5G	640K	19.5G	-	-	0%	0%
        zroot	53.5G	1.29G	52.2G	-	-	0%	2%	1.00x	ONLINE	-
                raidz1	53.5G	1.29G	52.2G	-	-	0%	2%
                da0p3	-	-	-	-	-	-	-
                da1p3	-	-	-	-	-	-	-
                da2p3	-	-	-	-	-	-	-
                raidz1	53.5G	1.29G	52.2G	-	-	0%	2%
                da4p3	-	-	-	-	-	-	-
                da5p3	-	-	-	-	-	-	-
                da6p3	-	-	-	-	-	-	-
        Output:
            [
                {
                    'pool': 'data', 
                    'pool_data': [
                        {
                            'method': 'stripe',
                            'device': ['da3']
                        }
                    ]
                },
                {
                    'pool': 'zroot',
                    'pool_data': [
                        {
                            'method': 'raidz1',
                            'device': ['da0p3', 'da1p3', 'da2p3']
                        },
                        {
                            'method': 'raidz1',
                            'device': ['da4p3', 'da5p3', 'da6p3']
                        }
                    ]
                }
            ]
        """

        result = []
        tmp = subprocess.run('ssh root@{} zpool list -Hv'.format(node_ip), shell=True, encoding='utf8', capture_output=True)
        _ = tmp.stderr
        if not tmp.stdout:
            return 'nothing'

        shell_result = tmp.stdout.split('\n')

        del shell_result[-1]

        pool_idx_list = ShellParser._get_pool_idx(shell_result)
        pool_list = ShellParser._split_by_pool(shell_result, pool_idx_list)

        save_point =[]
        for idx, data in enumerate(pool_list):
            save_flag=True
            save_idx=[]
            row_idx= 0
            for i in data:
                row_idx+=1
                tmp_str = i.split('\t')[1]
                if 'raid' in tmp_str or 'mirror' in tmp_str:
                    if not save_flag:
                        save_idx.append(row_idx-1)
                    save_flag=False
            save_idx.append(len(data))          
            save_point.append(save_idx)  

        result = []

        for idx, data in enumerate(pool_list):
            res_dict = {
            "pool": "",
            "pool_data": []
                }
            
            pool_list=[]
            method_dict={}
            device_list=[]
            last_idx= 0
            for i in data:
                last_idx+=1

                tmp_str = i.split('\t')[1]
                if not i.startswith('\t'): 
                        pool_name = i.split('\t')[0]
                        res_dict['pool'] = pool_name
                        
                else:
                    tmp_str = i.split('\t')[1]
                    if 'raid' in tmp_str or 'mirror' in tmp_str:
                        method_dict["method"]=tmp_str
                            
                    else:
                        device_list.append(tmp_str)               
                        
                if last_idx in save_point[idx]:
                    if not method_dict.get("method"):
                            method_dict["method"]='stripe'
                    method_dict["device"]=device_list
                    pool_list.append(method_dict)
                    device_list=[]
                    method_dict={}

                res_dict['pool_data']=pool_list
            result.append(res_dict)

        return result


    @staticmethod
    def ashift_value_parser(input_value):
        ashift_list = input_value.split(":")
        ashift = ashift_list[-1].strip()
        
        return ashift

    @staticmethod
    def get_bootfs_parser(node_ip):
        result = subprocess.run('ssh root@{} zpool get -H bootfs'.format(node_ip), shell=True, encoding='utf8', capture_output=True)
        _ = result.stderr
        tmp_list = result.stdout.split('\n')

        for line in tmp_list:
            bootfs_list = line.split('\t')
            if '-' not in bootfs_list:
                break
        
        return bootfs_list

if __name__ == '__main__':
    result = ShellParser.get_bootfs_parser('192.168.10.68')
    print(result)