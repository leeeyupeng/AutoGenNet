    public static void Write(this RakNet.BitStream bs, {name} data{name})
    {
{write}
    }

    public static void Read(this RakNet.BitStream bs, out {name} data{name})
    {
{read}
    }

    public static void WriteCompressed(this RakNet.BitStream bs, {name} data{name})
    {
{writeCompressed}
    }

    public static void ReadCompressed(this RakNet.BitStream bs, out {name} data{name})
    {
{readCompressed}
    }

    public static void Read(this RakNet.BitStream bs, out List<{name}> dataList)
    {
        dataList = new List<{name}>();
        while (bs.GetNumberOfUnreadBits() > 0)
        {
            {name} data;
            bs.Read(out data);
            dataList.Add(data);
        }
    }

    public static void ReadCompressed(this RakNet.BitStream bs, out List<{name}> dataList)
    {
        dataList = new List<{name}>();
        while (bs.GetNumberOfUnreadBits() > 0)
        {
            {name} data;
            bs.Read(out data);
            dataList.Add(data);
        }
    }
